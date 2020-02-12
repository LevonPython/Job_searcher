from bs4 import BeautifulSoup
import requests
import csv
from requests_html import HTMLSession
import time
from selenium import webdriver


class Exceptions(Exception):
    pass


class JobsScrapping:
    __slots__ = "staff_url", "jobfinder_url", "i_job", "hr_url", "careercenter", "myjob", 'data_csv', 'keyword'

    def __init__(self, staff_url, jobfinder_url, i_job, hr_url, careercenter, myjob, data_csv, keyword):
        self.staff_url = staff_url
        self.jobfinder_url = jobfinder_url
        self.i_job = i_job
        self.hr_url = hr_url
        self.careercenter = careercenter
        self.myjob = myjob
        self.data_csv = data_csv
        self.keyword = keyword

    def csv_file_open(self):
        with open(self.data_csv, 'w', newline='', encoding="utf-8") as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=[
                'title', 'job_title_eng', 'company_name', 'deadline', 'employment_term', 'job_type',
                'category', 'location', 'job_link'])
            csv_writer.writeheader()
            self.staff_am_scrap(csv_writer, 15)
            self.hr_am_scrap(csv_writer)
            self.jobfinder_am_scrap(csv_writer)
            self.i_job_scrap(csv_writer)
            self.careercenter_am_scrap(csv_writer)
            self.my_job_am(csv_writer)
            finished = time.time()
            print(f"Minutes spent to search {(finished - started)/60:.2f}")

    def csv_writing(self, title, job_title_eng, company_name, deadline, employment_term, job_type,
                    category, location, job_link, csv_writer):
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

    def staff_am_scrap(self, csv_writer, step=50, title='', deadline='', employment_term='',
                       job_type='', category='', location=''):
        print("started ...")

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
                        # openning each job announcment link
                        url_open = requests.get(job_link).text
                        url_soup = BeautifulSoup(url_open, 'lxml')
                        # if content includes a keyword not in position but in Required qualifications
                        find_skills = url_soup.find("div", class_="soft-skills-list clearfix")
                        prof = find_skills.text.strip('  ').lower().split()
                        # CHECK the keyword
                        if (self.keyword in prof) or (self.keyword in job_title_eng):
                            # grap necessary info from each announcement
                            company_name = url_soup.find('h1', class_="job_company_title").text
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
                            self.csv_writing(title, job_title_eng, company_name, deadline, employment_term, job_type,
                                             category, location, job_link, csv_writer)
                    except Exception as err:
                        Exceptions(f"ERROR {err}")
                        continue
        print("staff.am scraped successfully")

    def jobfinder_am_scrap(self, csv_writer, job_title_eng=''):
        source = requests.get(self.jobfinder_url).text
        soup = BeautifulSoup(source, "lxml")
        job_list = soup.find('table', class_="grid")

        for job in job_list.select('tr'):  # CSS selector

            find_title = job.select_one('td:nth-last-child(3)')
            try:
                title = find_title.a.text.strip()
            except Exception as err:
                Exceptions(f"ERROR {err}")
                continue

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

                # if content includes a keyword not in position but in Required qualifications
                req_qual = job_soup.find(
                    'span', id="ctl00_bdyPlaceHolde_jfpanelViewJob_jfJobPreview_lblRequiredQualifications").text
                if self.keyword in req_qual.lower() or self.keyword in title.lower():
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
                    self.csv_writing(title, job_title_eng, company_name, deadline, employment_term, job_type,
                                     category, location, job_link, csv_writer)
            except Exception as err:
                Exceptions(f"ERROR {err}")
                continue
        print("jobfinder.am scraped successfully")

    def i_job_scrap(self, csv_writer, employment_term='', category=''):
        driver = webdriver.Chrome()
        driver.get(self.i_job.format(self.keyword))
        time.sleep(5)
        for i in driver.find_elements_by_css_selector(
                '#primary > div.container.content-area > div > div > ul > li'):
            link = driver.find_element_by_class_name('job_listing-clickbox')
            job_link = link.get_attribute('href')
            job_info = i.text.split('\n')
            title = job_info[0]
            job_title_eng = title
            company_name = job_info[1]
            location = job_info[2]
            job_type = job_info[3]
            deadline = job_info[-1][7:].strip()
            self.csv_writing(title, job_title_eng, company_name, deadline, employment_term, job_type,
                             category, location, job_link, csv_writer)
        print("ijob.am scraped successfully")

    def hr_am_scrap(self, csv_writer, job_title_eng='', employment_term='',
                    job_type='', category='', location=''):
        driver = webdriver.Chrome()
        driver.get(self.hr_url)
        time.sleep(5)
        page_num = 1
        next_page = driver.find_element_by_css_selector('div#vacancy_pagination > a:nth-child({})'.format(page_num))
        while next_page:
            print(f"page number - {page_num}")
            try:
                for i in driver.find_elements_by_css_selector('section#vacancy_wrapper div.vacancy-item'):
                    desc = i.text.split('\n')
                    title = ','.join(desc[:-3]).lower().strip()
                    if self.keyword in title:
                        i.click()
                        time.sleep(3)
                        find_link = i.find_element_by_css_selector(
                            'section#vacancy_wrapper div.vacancy-description > a')
                        job_link = find_link.get_attribute('href')
                        company_name = desc[-3]
                        deadline = desc[-1]
                        self.csv_writing(title, job_title_eng, company_name, deadline, employment_term, job_type,
                                         category, location, job_link, csv_writer)
                page_num += 1
                next_page = driver.find_element_by_css_selector(
                    'div#vacancy_pagination > a:nth-child({})'.format(page_num))
                next_page.click()
                time.sleep(3)
            except Exception as err:
                print(f"pages ended -- {err}")
                break
        print("hr.am scraped successfully")

    def careercenter_am_scrap(self, csv_writer, employment_term='', job_type='',
                              category='', location=''):
        source = requests.get(self.careercenter)
        content = source.content
        res_ascii = content.decode('ascii')
        soup = BeautifulSoup(res_ascii, 'lxml')
        for job in soup.select('tr'):
            job_info = job.select_one('td>a')

            if job_info is not None:
                job_splitted = job_info.text.split(" / ")
                title = job_splitted[0]
                job_title_eng = title
                company_name = job_splitted[1]

                try:
                    find_deadline = job_info['title']
                    if not find_deadline[20] == ':':
                        deadline = find_deadline
                    else:
                        deadline = find_deadline[22:]
                except Exception as err:
                    Exceptions(f"ERROR {err}")
                    continue
                job_link = f"https://careercenter.am/{job_info['href']}"
                open_job = requests.get(job_link)
                new_content = open_job.content
                try:
                    new_res = new_content.decode('ascii')
                    new_soup = BeautifulSoup(new_res, 'lxml')
                    for elem in new_soup.select('p'):
                        # if content includes a keyword not in position but in Required qualifications
                        if self.keyword in elem.text.lower():
                            if elem.text.startswith("LOCATION:"):
                                location = elem.text
                            elif elem.text.startswith("DURATION:"):
                                employment_term = elem.text.split("DURATION:  ")[1].strip()
                            self.csv_writing(title, job_title_eng, company_name, deadline, employment_term, job_type,
                                             category, location, job_link, csv_writer)
                except Exception as err:
                    Exceptions(f"ERROR {err}")
                    continue
        print("careercenter.am scraped successfully")
    def my_job_am(self, csv_writer, employment_term='', job_type=''):
        page_num = 1
        source = requests.get(self.myjob.format(page_num)).text
        chek_list = []
        stop_here = 'double link'
        scrap_end = ''
        while source:
            try:
                soup = BeautifulSoup(source, 'lxml')
                for job in soup.find('div', class_="jobPageContainer"):
                    job_link = f"https://www.myjob.am/{job['href']}"
                    # check if the next page is not loaded back again to the first page
                    if job_link not in chek_list:
                        chek_list.append(job_link)
                        title = job.find('div', class_="shortJobPosition").text
                        job_title_eng = title
                        company_name = job.find('div', class_='shortJobCompany').text
                        location = job.find('div', class_="shortJobRightPart").text
                        # grap from each job page
                        job_source = requests.get(job_link).text
                        job_soup = BeautifulSoup(job_source, 'lxml')
                        find_category = job_soup.find('div', class_="fullJobTextsShort").text
                        category = find_category.split(location)[0]
                        deadline = find_category.split(location)[1]
                        for i in job_soup.find_all('div', class_="fullJobTextLong"):
                            if self.keyword in i.text.lower():
                                self.csv_writing(title, job_title_eng, company_name, deadline, employment_term,
                                                 job_type, category, location, job_link, csv_writer)
                    else:
                        scrap_end = stop_here
            except Exception as err:
                print(f"ERROR {err}")
                break

            if scrap_end == stop_here:
                break
            page_num += 1
            source = requests.get(self.myjob.format(page_num)).text
            print(page_num)
        print("myjob.am scraped successfully")


if __name__ == "__main__":
    Staff_url = "https://staff.am/en/jobs?page={}&per-page=50"
    Jobfinder_url = "http://jobfinder.am/default.aspx"
    Hr_url = "http://hr.am/"
    I_job = "http://ijob.am/job-list/?search_keywords={}" \
            "&search_location=&search_categories%5B%5D=&submit=Search&filter_job_type%5B%5D="
    Careercenter = "https://careercenter.am/ccidxann.php"
    My_job_url = "https://www.myjob.am/?pg={}"
    Keyword = input("Hint: keywords examples: intern, accountant, lawyer, engineer,"
                    " administrator, python\n\nPlease fill position:  ")
    started = time.time()
    Data_csv = f"{Keyword}_Jobs_advanced_search.csv"
    res = JobsScrapping(Staff_url, Jobfinder_url, I_job, Hr_url, Careercenter, My_job_url, Data_csv, Keyword)
    res.csv_file_open()
