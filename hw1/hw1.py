#!/usr/bin/env python
# coding: utf-8

# In[73]:


# I have used the code from the course website and consult with other classmates, but I write the code by myself.


from typing import List
import requests
from typing import Dict, Tuple
from typing import Optional
from bs4 import BeautifulSoup

# In[74]:


import re

# class meeting time on exam web: e.g 8:00 MW
TIME_DAYS = re.compile('(\d{1,2}):(\d\d)\s+([A-Za-z]+)')
TIME = re.compile('(\d{1,2}):(\d\d)\s*([AaPp]\.?\s*[Mm]\.?)?')

# `<program><number>-<section>`
Course = re.compile('([A-Za-z]+)(\d{1,3}[A-Za-z]*?)-(\d*)')


# In[75]:


# normalize the time and the day

def norm_time(hour: str, minute: str, period: Optional[str] = None) -> int:
    h = int(hour)
    m = int(minute)

    if period and period[0].upper() == 'P':
        h += 12
    # On the website, the class time has no period, but every afternoon class starts before 7
    elif h < 7:
        h += 12

    return h * 100 + m


def norm_days(days: str) -> int:
    DAYS = [('M', 0), ('TU', 1), ('W', 2), ('TH', 3), ('F', 4)]
    days = days.upper()
    b = ['0'] * 5

    for d, i in DAYS:
        if d in days:
            b[i] = '1'
            days = days.replace(d, '')

    if 'T' in days:
        b[1] = '1'
        days = days.replace('T', '')

    return int(''.join(b), 2)


# In[76]:


# Retrieve the infor from the website

# Write a function that takes the exam schedule URL and returns a dictionary where the key is the normalized class meeting time
# and the value is its exam schedule information.
def extract_exam_schedule(url) -> Dict[Tuple[int, int], Tuple[str, str, str]]:
    r = requests.get(url)
    html = BeautifulSoup(r.text, 'html.parser')
    tbody = html.find('tbody')
    schedule = {}

    for tr in tbody.find_all('tr'):
        tds = tr.find_all('td')
        class_time = tds[0].string.strip()
        m = TIME_DAYS.match(class_time)
        if m:
            time = norm_time(int(m.group(1)), int(m.group(2)))
            days = norm_days(m.group(3))
            key = (time, days)
            exam_day = tds[1].string.strip()
            exam_date = tds[2].string.strip()
            exam_time = tds[3].string.strip()
            schedule[key] = (exam_day, exam_date, exam_time)

    return schedule


# Write a function that takes the class schedule URL and returns a dictionary where the key is the class ID in OPUS
def extract_class_schedule(url) -> Dict[int, Tuple[str, str, str, str, int, str, str, str]]:
    r = requests.get(url)
    html = BeautifulSoup(r.text, 'html.parser')
    schedule = {}

    for tr in html.find_all('tr'):
        td1 = tr.find_all('td')
        if len(td1) < 10: continue

        program = td1[0].string.strip()
        number = td1[1].string.strip()
        section = td1[2].string.strip()
        title = td1[5].text.strip()
        opus = int(td1[6].string)

        td2 = td1[9].find_all('td')
        days = td2[0].string
        if days is None:
            continue
        else:
            days = days.strip()
        time = td2[1].text.strip()
        instructor = td2[3].string

        schedule[opus] = (program, number, section, title, opus, days, time, instructor)

    return schedule


# In[77]:


def create_html(html_file: str, program: str, exam_schedule: Dict[Tuple[int, int], Tuple[str, str, str]],
                class_schedule: Dict[int, Tuple[str, str, str, str, int, str, str, str]]):
    soup = BeautifulSoup("<html></html>", 'html.parser')
    html = soup.html

    table = soup.new_tag('table')
    html.append(table)

    thead = soup.new_tag('thead')
    table.append(thead)

    tr = soup.new_tag('tr')
    thead.append(tr)

    for s in ['Couse', 'Opus', 'Title', 'Instructor', 'Exam Schedule']:
        td = soup.new_tag('td')
        td.string = s
        tr.append(td)

    tbody = soup.new_tag('tbody')
    table.append(tbody)

    for k, v in class_schedule.items():
        if v[0] != program: continue
        course = v[0] + v[1] + '-' + v[2]
        opus = str(v[4])
        title = v[3]
        instructor = str(v[-1])
        t = get_exam_schedule(k, exam_schedule, class_schedule)
        if t is None: continue
        ex_schedule = ', '.join(list(t))

        tr = soup.new_tag('tr')
        tbody.append(tr)

        for s in [course, opus, title, instructor, ex_schedule]:
            td = soup.new_tag('td')
            td.string = s
            tr.append(td)

    with open(html_file, 'w') as fout:
        fout.write(soup.prettify())


# In[78]:


# a function that takes exam_schedule, class_schedule, and an OPUS class number,
# and returns the exam schedule of the corresponding class if available; otherwise, None:
def get_exam_schedule(opus: int, exam_schedule: Dict[Tuple[int, int], Tuple[str, str, str]],
                      class_schedule: Dict[int, Tuple[str, str, str, str, int, str, str, str]]) -> Tuple[str, str, str]:
    s = class_schedule.get(opus, None)
    if s is None: return None
    days = norm_days(s[5])
    m = TIME.match(s[6])
    time = norm_time(m.group(1), m.group(2))
    key = (time, days)
    return exam_schedule.get(key, None)


# In[79]:


def get_opus_id(course_id: str, class_schedule: Dict[int, Tuple[str, str, str, str, int, str, str, str]]):
    s = Course.match(course_id)
    program = s.group(1)
    number = s.group(2)
    section = s.group(3)

    list = [opus for opus, classes in class_schedule.items() if
            classes[0] == program and classes[1] == number and classes[2] == section]
    opus_id = list[0]
    return opus_id


# In[80]:


def generate_html_files(url_exam: str, url_class: str, html_dir: str):
    """
    Generates one HTML file per program (e.g., QTM) under the `html/` directory
    that displays the exam and class information together for that program.
    :param url_exam: the URL to the exam schedule page.
    :param url_class: the URL to the class schedule page.
    :param html_dir: the directory path where the HTML files are to be generated.
    """
    # TODO: to be updated
    url_exam = 'http://registrar.emory.edu/faculty-staff/exam-schedule/spring-2019.html'
    url_class = 'http://atlas.college.emory.edu/class-schedules/spring-2019.php'
    exam_schedule = extract_exam_schedule(url_exam)
    class_schedule = extract_class_schedule(url_class)

    s = set([v[0] for k, v in class_schedule.items()])

    for q in sorted(list(s)):
        create_html('html/%s.html' % q.lower(), '%s' % q.upper(), exam_schedule, class_schedule)

    pass


# In[90]:


def print_exam_schedule(course_ids: List[str]):
    """
    Prints the exam schedules of the input courses.
    :param course_id: `<program><number>-<section>` (e.g., `QTM385-1`)
    """
    url_exam = 'http://registrar.emory.edu/faculty-staff/exam-schedule/spring-2019.html'
    url_class = 'http://atlas.college.emory.edu/class-schedules/spring-2019.php'
    exam_schedule = extract_exam_schedule(url_exam)
    class_schedule = extract_class_schedule(url_class)
    # TODO: to be updated
    for course_id in course_ids:
        opus_id = get_opus_id(course_id, class_schedule)
        class_exam_schedule = get_exam_schedule(opus_id, exam_schedule, class_schedule)
        print(class_exam_schedule)


# In[91]:


if __name__ == '__main__':
    url_exam = 'http://registrar.emory.edu/faculty-staff/exam-schedule/spring-2019.html'
    url_class = 'http://atlas.college.emory.edu/class-schedules/spring-2019.php'
    html_dir = 'html/'
    exam_schedule = extract_exam_schedule(url_exam)
    class_schedule = extract_class_schedule(url_class)
    generate_html_files(url_exam, url_class, html_dir)
    print_exam_schedule(['AAS100-1', 'QTM385-1'])





