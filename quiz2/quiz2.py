# Add all necessary contents and update the instructor_by_academic_year function
# that takes course_info as input and plots the number of instructors by academic years.
import csv

csv_file = 'cs_courses_2008_2018.csv'

with open(csv_file) as fin:
    reader = csv.reader(fin)
    course_info = [row for i, row in enumerate(reader)]

from types import SimpleNamespace


def info(row):
    # term is normalized to (year, term_id) (e.g., 5181 -> (2018, 1))
    # term_id = 1: Spring, 6: Summer, 9: Fall
    r = row[0]
    term = (2000 + int((int(r) - 5000) / 10), int(r[-1]))

    # name = lastname,firstname
    r = row[12].split(',')
    instructor = (r[0].strip(), r[1].strip())

    return SimpleNamespace(
        term=term,
        subject=row[3].strip(),
        catalog=row[4].strip(),
        section=row[5].strip(),
        title=row[6].strip(),
        min_hours=int(row[8]),
        max_hours=int(row[9]),
        enrollment=int(row[11]),
        instructor=instructor)


def skip(i, row):
    return i == 0 or \
           int(row[11]) == 0 or \
           row[12].strip() == '' or \
           row[14].strip() != 'Active'


def term_to_year(term):
    """
    :param term: a tuple of (year, term_id).
    """
    return term[0] if term[1] == 9 else term[0] - 1


def load_course_info(csv_file):
    with open(csv_file) as fin:
        reader = csv.reader(fin)
        course_info = [info(row) for i, row in enumerate(reader) if not skip(i, row)]

    return course_info


def instructor_academic_year(course_info):
    inst = {}
    for c in course_info:
        year = term_to_year(c.term)
        if year in inst:
            inst[year].add(c.instructor)
        else:
            inst[year] = {c.instructor}

    return inst


for k, v in sorted(d.items()): print(k, len(v))
d

import matplotlib.pyplot as plt

d = instructor_academic_year(course_info)


def plot_dict(d):
    xs, ys = zip(*[(k, v) for k, v in sorted(d.items())])
    # k, year; v,count
    plt.scatter(xs, ys)
    plt.plot(xs, ys)
    plt.grid(b='on')
    plt.show()


## I can print out the result but can not print it out
plot_dict(d)

if __name__ == '__main__':
    csv_file = 'cs_courses_2008_2018.csv'
    course_info = load_course_info(csv_file)
    instructor_academic_year(course_info)


