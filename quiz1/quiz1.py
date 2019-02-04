import requests
from bs4 import BeautifulSoup
import re
from typing import Optional, Dict, Tuple


# normalize class time to military time for afternoon classes
def norm_time(hour: str, minute: str, period: Optional[str] = None) -> int:
    h = int(hour)
    m = int(minute)

    if period and period[0].upper() == 'P':
        h += 12
    # On the website, the class time has no period, but every afternoon class starts before 7
    elif h < 7:
        h += 12

    return h * 100 + m


# nromalize day into binary form
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


def extract_exam_schedule(url) -> Dict[Tuple[int, int], Tuple[str, str, str]]:
    r = requests.get(url)
    html = BeautifulSoup(r.text, 'html.parser')
    tbody = html.find('tbody')
    schedule = {}
    TIME_DAYS = re.compile('(\d{1,2}):(\d\d)\s+([A-Za-z]+)')
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


if __name__ == '__main__':
    url = 'http://registrar.emory.edu/faculty-staff/exam-schedule/spring-2019.html'
    exam_schedule = extract_exam_schedule(url)
    for k, v in exam_schedule.items():
        print('%14s : %s' % (k, v))