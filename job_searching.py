from bs4 import BeautifulSoup
import requests
import csv


class JobsScrapping:
    __slots__ = "url", 'data_csv', 'keyword'

    def __init__(self, url, data_csv, keyword):
        self.url = url
        self.data_csv = data_csv
        self.keyword = keyword

    def scrapping(self, step=50):

        with open(self.data_csv, 'w', newline='', encoding="utf-8") as csv_file:
            # csv_writer = csv.writer(csv_file)
            csv_writer = csv.DictWriter(csv_file, fieldnames=['title', 'job_title_eng', 'deadline', 'employment_term',
                                                              'job_type', 'category', 'location', 'job_link'])
            csv_writer.writeheader()

            for page in range(0, step):
                source = requests.get(self.url.format(page + 1)).text
                soup = BeautifulSoup(source, 'lxml')
                job_list = soup.find_all('div', attrs={'id': 'w0', 'class': 'list-view'})
                for more in job_list:
                    see_more = more.find_all('div',
                                             class_="job-inner-right text-right load-more-container pull-right")
                    for i in range(len(see_more)):
                        link = see_more[i].a['href']
                        job_link = f"https://staff.am{link}"
                        job_title_eng = link.split('en/')[1].lower()

                        try:
                            if self.keyword in job_title_eng:
                                # openning each job announcment link
                                url_open = requests.get(job_link).text
                                url_soup = BeautifulSoup(url_open, 'lxml')

                                # if content includes a keyword not in position but in Required qualifications
                                # find_skills = url_soup.find("div", class_="soft-skills-list clearfix")
                                # prof = ''
                                # for skills in find_skills:
                                #     prof = skills.text.strip('  ').lower().split()
                                #     if (self.keyword in prof) or (self.keyword in job_title_eng):
                                #         print(f"{self.keyword} keyword matches in"
                                #               f"{job_title_eng} required position qualifications")

                                # grap necessary info from each announcement
                                title_origin = url_soup.find_all('div', class_="col-lg-8")
                                for k in range(len(title_origin)):
                                    title_arm = title_origin[k].h2
                                    if title_arm is not None:
                                        pass
                                        title = title_arm.text.strip()

                                deadline_find = url_soup.find_all('div', class_="col-lg-4 apply-btn-top")
                                for t in range(len(deadline_find)):
                                    result = deadline_find[t].p
                                    if result is not None:
                                        deadline = result.text.split(':')[1].strip().replace('\n', ' ')

                                terms = url_soup.find_all('div', class_="col-lg-6 job-info")
                                for n in range(len(terms)):
                                    elem_fst = terms[n].p.text.strip().split(':')
                                    elem_scd = terms[n].text.strip().split()
                                    if elem_fst[0] == "Employment term":
                                        employment_term = elem_fst[1].strip()
                                    elif elem_fst[0] == "Job type":
                                        job_type = elem_fst[1].strip()
                                    if elem_scd[3] == 'Category:':
                                        category = elem_scd[4].strip()
                                    elif elem_scd[4] == "Location:":
                                        location = elem_scd[5].strip()
                                jobs_info = [{'title': title,
                                              'job_title_eng': job_title_eng,
                                              'deadline': deadline,
                                              'employment_term': employment_term,
                                              'job_type': job_type,
                                              'category': category,
                                              'location': location,
                                              'job_link': job_link
                                              }]
                                for jobs in jobs_info:
                                    csv_writer.writerow(jobs)
                        except Exception as err:
                            print(err)
                            continue


if __name__ == "__main__":
    Url = "https://staff.am/en/jobs?page={}&per-page=50"
    # Keyword = 'intern'
    Keyword = 'accountant'
    # Keyword = 'python'
    # Keyword = 'administrator'
    Data_csv = f"{Keyword}_Jobs.csv"
    res = JobsScrapping(Url, Data_csv, Keyword)
    res.scrapping(15)
