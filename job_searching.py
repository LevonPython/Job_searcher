from bs4 import BeautifulSoup
import requests
import csv


class Exceptions(Exception):
    pass


class JobsScrapping:
    __slots__ = "staff_url", "jobdinfer_url", "hr_url", 'data_csv', 'keyword'

    def __init__(self, staff_url, jobdinfer_url, hr_url, data_csv, keyword):
        self.staff_url = staff_url
        self.jobdinfer_url = jobdinfer_url
        self.hr_url = hr_url
        self.data_csv = data_csv
        self.keyword = keyword

    def csv_file_open(self):
        with open(self.data_csv, 'w', newline='', encoding="utf-8") as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=[
                'title', 'job_title_eng', 'company_name', 'deadline', 'employment_term', 'job_type',
                'category', 'location', 'job_link'])
            csv_writer.writeheader()
            self.staff_am_scrap(csv_writer, 15)
            # self.hr_am_scrap(csv_writer, 32)
            self.jobfinder_am_scrap(csv_writer)

    # ----------------------------- S T A F F . A M -----------------------------------------------------------
    def staff_am_scrap(self, csv_writer, step=50,
                       title='', company_name='', deadline='', employment_term='',
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
                                          'company_name': company_name,
                                          'deadline': deadline,
                                          'employment_term': employment_term,
                                          'job_type': job_type,
                                          'category': category,
                                          'location': location,
                                          'job_link': job_link,
                                          }]
                            for jobs in jobs_info:
                                csv_writer.writerow(jobs)
                    except Exception as err:
                        Exceptions(f"ERROR {err}")
                        continue

    # ----------------------------- J O B F I N D E R  . A M ---------------------------------------------------------
    def jobfinder_am_scrap(self, csv_writer, job_title_eng=''):
        source = requests.get(self.jobdinfer_url).text
        soup = BeautifulSoup(source, "lxml")
        job_list = soup.find('table', class_="grid")

        for job in job_list.select('tr'):  # CSS selector

            find_title = job.select_one('td:nth-last-child(3)')
            try:
                title = find_title.a.text.strip()
            except Exception as err:
                Exceptions(f"ERROR {err}")
                continue
            if self.keyword in title.lower():
                company = job.select_one('td:nth-last-child(2)')
                try:
                    company_name = company.span.text
                except Exception as err:
                    Exceptions(f"ERROR {err}")
                    continue

                find_deadline = job.select_one('td:nth-child(3)')
                try:
                    deadline = find_deadline.text.strip()
                except Exception as err:
                    Exceptions(f"ERROR {err}")
                    continue

                find_job_link = job.select_one('td:nth-last-child(3)')
                try:
                    job_link = 'http://jobfinder.am/{}'.format(
                        find_job_link.find('a', title="Display in new window")['href'])

                    # opening each job description
                    open_job_link = requests.get(job_link).text
                    job_soup = BeautifulSoup(open_job_link, 'lxml')
                    table = job_soup.find('table', class_="fieldtable")
                    location = table.find(
                        'span', id="ctl00_bdyPlaceHolde_jfpanelViewJob_jfJobPreview_lblLocation").text
                    category = table.find(
                        'span', id="ctl00_bdyPlaceHolde_jfpanelViewJob_jfJobPreview_lblCategory").text
                    job_type = table.find(
                        'span', id="ctl00_bdyPlaceHolde_jfpanelViewJob_jfJobPreview_lblPositionType").text
                    if job_type in ("Full Time", "Լրիվ դրույք", "Полная ставка"):
                        employment_term = "Permanent"
                    elif job_type in "Internship":
                        employment_term = "Part time"
                    elif job_type in "Casual":
                        employment_term = "Part time"
                    elif job_type in "Պրակտիկա":
                        employment_term = "Permanent"
                    else:
                        employment_term = "Other"

                    jobs_info = [{'title': title,
                                  'job_title_eng': job_title_eng,
                                  'company_name': company_name,
                                  'deadline': deadline,
                                  'employment_term': employment_term,
                                  'job_type': job_type,
                                  'category': category,
                                  'location': location,
                                  'job_link': job_link,
                                  }]
                    for jobs in jobs_info:
                        csv_writer.writerow(jobs)

                    # # if content includes a keyword not in position but in Required qualifications
                    # req_qual = job_soup.find(
                    #     'span', id="ctl00_bdyPlaceHolde_jfpanelViewJob_jfJobPreview_lblRequiredQualifications").text
                    # if self.keyword in req_qual.lower() or self.keyword in title.lower():
                    #     for jobs in jobs_info:
                    #         csv_writer.writerow(jobs)

                except Exception as err:
                    Exceptions(f"ERROR {err}")
                    continue

    # ----------------------------- H R . A M -----------------------------------------------------------
    def hr_am_scrap(self, csv_writer, step=50):
        pass
        # source = requests.get(self.hr_url).text
        # soup = BeautifulSoup(source, 'html.parser')
        # print(soup.prettify())
        # job = soup.find('div', class_="vacancy-item")
        # js , can't open the job content
        # opens = requests.get(job)
        # so = BeautifulSoup(opens, 'lxml')
        # title = job_list.find_all('div', class_="title")
        #     print(title)
        # print(job)


if __name__ == "__main__":
    Staff_url = "https://staff.am/en/jobs?page={}&per-page=50"
    Jobdinfer_url = "http://jobfinder.am/default.aspx"
    Hr_url = "http://hr.am/"
    # Keyword = 'intern'
    # Keyword = 'accountant'
    Keyword = 'python'
    # Keyword = 'administrator'
    # Keyword = input("Please fill position: ")
    Data_csv = f"{Keyword}_Jobs.csv"
    res = JobsScrapping(Staff_url, Jobdinfer_url, Hr_url, Data_csv, Keyword)
    res.csv_file_open()
