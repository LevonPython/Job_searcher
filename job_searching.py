from bs4 import BeautifulSoup
import requests
import csv


class JobsScrapping:
    __slots__ = "staff_url", "hr_url", 'data_csv', 'keyword'

    def __init__(self, staff_url, hr_url, data_csv, keyword):
        self.staff_url = staff_url
        self.hr_url = hr_url
        self.data_csv = data_csv
        self.keyword = keyword

    def csv_file_open(self):
        with open(self.data_csv, 'w', newline='', encoding="utf-8") as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=['title', 'job_title_eng', 'deadline', 'employment_term',
                                                              'job_type', 'category', 'location', 'job_link'])
            csv_writer.writeheader()
            self.staff_am_scrap(csv_writer, 15)
            self.hr_am_scrap(csv_writer, 32)

    def staff_am_scrap(self, csv_writer, step=50,
                       title='', deadline='', employment_term='',
                       job_type='', category='', location=''):

        for page in range(0, step):
            source = requests.get(self.staff_url.format(page + 1)).text
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

    def hr_am_scrap(self, csv_writer, step=50):
        source = requests.get(self.hr_url).text
        soup = BeautifulSoup(source, 'lxml')
        # job = soup.find('div', class_="logo")
        # js , can't open the job content
        # opens = requests.get(job)
        # so = BeautifulSoup(opens, 'lxml')
        # title = job_list.find_all('div', class_="title")
        #     print(title)
        # print(job)


if __name__ == "__main__":
    Staff_url = "https://staff.am/en/jobs?page={}&per-page=50"
    Hr_url = "http://hr.am/"
    # Keyword = 'intern'
    # Keyword = 'accountant'
    Keyword = 'python'
    # Keyword = 'administrator'
    # Keyword = input("Please fill position: ")
    Data_csv = f"{Keyword}_Jobs.csv"
    res = JobsScrapping(Staff_url, Hr_url, Data_csv, Keyword)
    res.csv_file_open()
