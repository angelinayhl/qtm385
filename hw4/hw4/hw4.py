from bs4 import BeautifulSoup
import requests
import re

## Time Pattern
TIME = re.compile('(\d{1,2}):(\d\d)\s*([AaPp]\.?\s*[Mm]\.?)?')
TIME_DAYS = re.compile('(\d{1,2}):(\d\d)\s+([A-Za-z]+)')

## Normalization for day
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

## Base for extract exam schedule
from typing import Dict, Tuple
from typing import Optional

def norm_time(hour: str, minute: str, period: Optional[str] = None) -> int:
    hr = int(hour)
    mi = int(minute)

    if period:
        if period[0].upper() == 'P':
            hr += 12

    return hr * 100 + mi

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
            key  = (time, days)
            exam_day  = tds[1].string.strip()
            exam_date = tds[2].string.strip()
            exam_time = tds[3].string.strip()
            schedule[key] = (exam_day, exam_date, exam_time)

    return schedule

## Base for extract class schedule
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

## Function for get exam schedule
def get_exam_schedule(opus: int, exam_schedule: Dict[Tuple[int, int], Tuple[str, str, str]], class_schedule: Dict[int, Tuple[str, str, str, str, int, str, str, str]]) -> Tuple[str, str, str]:
    s = class_schedule.get(opus, None)
    if s is None: return None
    days = norm_days(s[5])
    m = TIME.match(s[6])
    time = norm_time(m.group(1), m.group(2))
    key = (time, days)
    return exam_schedule.get(key, None)

ID = re.compile('([A-Za-z]+)(\d\d\d[A-Za-z]*)-([A-Za-z]*\d*)')


def get_class_opus_id(coursename: str, class_schedule: Dict[int, Tuple[str, str, str, str, int, str, str, str]]) -> int:
    m = ID.match(coursename)
    program = m.group(1)
    number = m.group(2)
    section = m.group(3)

    ans = [opus for opus, classes in class_schedule.items() if classes[0] == program and classes[1] == number and classes[2] == section][0]
    return ans



def print_exam_schedule(course_id: str):
    """
    Prints the exam schedules of the input courses.
    :param course_id: `<program><number>-<section>` (e.g., `QTM385-1`)
    """
    url_exam = 'http://registrar.emory.edu/faculty-staff/exam-schedule/spring-2019.html'
    url_class = 'http://atlas.college.emory.edu/class-schedules/spring-2019.php'
    exam_schedule = extract_exam_schedule(url_exam)
    class_schedule = extract_class_schedule(url_class)

    course_opus = get_class_opus_id(course_id, class_schedule)
    exam_opus_schedule = get_exam_schedule(course_opus, exam_schedule, class_schedule)
    return ', '.join(list(exam_opus_schedule))

def lambda_handler(event, context):
    course = event['course']
    schedule = print_exam_schedule(course)
    return schedule