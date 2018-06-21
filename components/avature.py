import os
from bs4 import UnicodeDammit
from bs4 import BeautifulSoup as bs4
import re
import requests
import pandas as pd
import zipfile


class PageFetchException(Exception):
    def __init__(self, message, url, status_code):
        super().__init__(message)
        self.url = url
        self.status_code = status_code


class ElementNotFoundException(Exception):
    def __init__(self, message, element):
        super().__init__(message)
        self.element = element


JD_HEADERS = re.compile(r"^((What|Who|Why) (Cisco|You|We))")

def _get_soups(zip_path):

    """
    Given a zipped folder, unzips
    Iterates through each unzipped file, reading and parsing HTML
    :param zip_path: path to zipfile
    :return:
    """

    zip_dir, zip_fname = os.path.split(zip_path)
    zip_fname = os.path.splitext(zip_fname)[0]
    zip_output_dir = os.path.join(zip_dir, zip_fname)

    if not os.path.isdir(zip_output_dir):  # Already extracted
        zip_file = zipfile.ZipFile(zip_path, 'r')
        zip_file.extractall(zip_output_dir)
        zip_file.close()

    files = []
    for sf in os.listdir(zip_output_dir):
        files.append(os.path.join(zip_output_dir, sf))

    soups = []
    for sf in files:
        try:
            with open(sf, 'rb') as html_file:
                html = html_file.read()
            soup = bs4(html, 'html.parser')
        except UnicodeError:
            with open(sf, 'rb') as html_file:
                html = html_file.read()
                html = UnicodeDammit(html).unicode_markup
            soup = bs4(html, 'html.parser')
        soups.append(soup)
    return soups


def extract_quickview(zip_path):
    soups = _get_soups(zip_path)
    people = []

    for soup in soups:
        fname = soup.find_all(class_=re.compile("firstName"))
        if fname:
            fname = fname[0].get_text()
        else:
            fname = ''

        lname = soup.find_all(class_=re.compile("lastName"))
        if lname:
            lname = lname[0].get_text()
        else:
            lname = ''

        title = soup.find_all(class_=re.compile("jobTitle"))
        if title:
            title = title[0].get_text()
        else:
            title = ''

        emp = soup.find_all(class_=re.compile("employer"))
        if emp:
            emp = emp[0].get_text()
        else:
            emp = ''

        res = soup.find_all(class_=re.compile("value attachment"))
        if res:
            res = res[0].get_text()
        else:
            res = ''

        td = {'fname': fname, 'lname': lname, 'title': title, 'emp': emp, 'Resume': res}
        people.append(td)

    df = pd.DataFrame(people)

    def split_or_none(x, splitter):
        l = x.split(splitter)
        if len(l) == 2:
            return l[1]
        else:
            return ''

    df['fname'] = df['fname'].apply(lambda x: split_or_none(x, 'First Name'))

    df['lname'] = df['lname'].apply(lambda x: split_or_none(x, 'Last Name'))

    df['emp'] = df['emp'].apply(lambda x: split_or_none(x, 'Current employer'))

    df['title'] = df['title'].apply(lambda x: split_or_none(x, 'Job title'))

    extra_n = re.compile('((\\n) ?){2,}')

    def trim_new_lines(x):
        y = extra_n.sub('\n', x)
        return y

    df['Resume'] = df['Resume'].apply(lambda x: trim_new_lines(x))

    return df


def _fetch_req(req_num):
    url = "https://jobs.cisco.com/jobs/ProjectDetail/{}".format(req_num)
    r = requests.get(url)
    if r.status_code != 200:
        raise PageFetchException(message="Getting page {} returned status code {}".format(url, r.status_code), url=url,
                                 status_code=r.status_code)
    page = bs4(r.content, 'html.parser')
    jd_element = page.find(class_="job_description")
    if not jd_element:
        raise ElementNotFoundException(message="Job Description Element Not Found", element="job_description")

    raw_text = jd_element.get_text("\n")  # Join with newlines
    text_lines = [line for line in raw_text.splitlines() if not JD_HEADERS.search(line)]
    return " ".join(text_lines)

