#!/usr/bin/env python3

import io
import xml.etree.ElementTree as ET
import argparse

ns = {'ns1': 'http://www.sifinfo.org/infrastructure/2.x',
      'ns2': 'http://stumo.transcriptcenter.com'}


class StudentInfo:
    def __init__(self, first_name, middle_name, last_name, ):
        self.last_name = last_name
        self.middle_name = middle_name
        self.first_name = first_name


class Grade:
    """A Wrapper for a single grade"""

    def __init__(self, year, grade_level, term, course_code, title, letter_grade, number_grade, comments, teacher_fn,
                 teacher_ln, school_name):
        self.teacher_ln = teacher_ln
        self.teacher_fn = teacher_fn
        self.comments = comments
        self.number_grade = number_grade

        # Special case for the Pandemic special grading
        self.letter_grade =  letter_grade if letter_grade is not None else "n/a"
        self.course_title = title
        self.course_code = course_code
        self.term = term
        self.year = year
        self.grade_level = grade_level
        self.school = school_name
        if (self.comments != None):
            self.comments = self.comments.strip()

    def __str__(self) -> str:
        return f"{self.year}-{self.term} (code: {self.course_code}) {self.course_title} {self.letter_grade}, {self.number_grade}, {self.comments}, {self.teacher_fn}, {self.teacher_ln} {self.school}"

    def pretty_print(self):
        return f"###{self.year}-{self.term}  {self.school} {self.grade_level} (code: {self.course_code}) {self.course_title} | Instructor: {self.teacher_fn} {self.teacher_ln}\n*Letter Grade*: {self.letter_grade} | *Grade:* {self.number_grade}\nComments: {self.comments} "

    def print_description(self):
        return f"{self.year}-{self.term}  {self.school} {self.grade_level} (code: {self.course_code}) {self.course_title}\nInstructor: {self.teacher_fn} {self.teacher_ln}\nLetter Grade: {self.letter_grade} \nGrade: {self.number_grade}\nComments:{self.comments} "

    def print_header(self):
        return f"{self.course_title} (code: {self.course_code}) {self.school}\n"

    def print_term_grade(self):
        return f"<em>{self.year}-{self.term} {self.grade_level}</em><br/>\n<b>{self.letter_grade}</b> / <b>{self.number_grade}</b>"

    def reporting_period(self):
        return f"{self.year}-{self.term}"

    def teacher_name(self):
        return f"{self.teacher_fn} {self.teacher_ln}"

    def format_comments(self):
        if (self.comments != None):
            return self.comments.replace('\n', ' ')
        else:
            return ''


def process_course(course, year):
    title = course.find(".//ns1:CourseTitle", ns).text
    course_code = course.find(".//ns1:CourseCode", ns).text
    mark_data = course.find(".//ns1:MarkData", ns)
    grade_level = course.find(".//ns1:GradeLevelWhenTaken/ns1:Code", ns).text
    letter_grade = mark_data.find("ns1:Letter", ns).text
    number_grade = mark_data.find("ns1:Percentage", ns).text
    comments = mark_data.find("ns1:Narrative", ns).text
    # get extended info
    extended_info = course.find("ns1:SIF_ExtendedElements", ns)
    term = extended_info.find("ns1:SIF_ExtendedElement[@Name='StoreCode']", ns).text
    teacher_fn = extended_info.find("ns1:SIF_ExtendedElement[@Name='InstructorFirstName']", ns).text
    teacher_ln = extended_info.find("ns1:SIF_ExtendedElement[@Name='InstructorLastName']", ns).text
    school_name = extended_info.find("ns1:SIF_ExtendedElement[@Name='SchoolName']", ns).text
    return Grade(year, grade_level, term, course_code, title, letter_grade, number_grade, comments, teacher_fn,
                 teacher_ln, school_name)


# Placeholder for markdown format for a list of grades
# Take the list and sort it with appropriate headers.
# TBD if we need to figure pass in meta data, whether we figure it out, or if we make assumptions.
def format_as_markdown(grades):
    pass


def process_data(xml_string):
    root = ET.fromstring(xml_string)
    ns_name = '{0}StudentDemographicRecord/{0}StudentPersonalData/{0}Name'.format('ns1:')
    name = root.find(ns_name, namespaces=ns)
    fn = name.find("ns1:FirstName", namespaces=ns).text
    mi = name.find("ns1:MiddleName", namespaces=ns).text
    ln = name.find("ns1:LastName", namespaces=ns).text
    (grades, years) = collect_grades(root)
    return (StudentInfo(fn, mi, ln), grades, years)


def generate_year_report(student_info, year, grades_by_course, schools, terms):
    output = io.StringIO()

    # Write Report Card Header
    output.write(f"<h1> {student_info.first_name}  {student_info.middle_name} {student_info.last_name}</h1>\n")
    output.write(f"<h1> {year}</h1>\n")
    for s in schools:
        output.write(f"<h2>{s}</h2>")

    for course in grades_by_course.keys():
        output.write('<div class="course">\n')
        output.write(f"<h2>{headers_by_course.get(course)}</h2>")

        course_by_term = organize_by_term(grades_by_course[course])

        grades_table = generate_grades_table(course_by_term, terms)
        output.write(grades_table)
        comments_table = generate_comments_table(course_by_term, terms)
        output.write(comments_table)
        output.write("</div>\n")
    return output.getvalue()


def generate_grades_table(course_by_term, terms):
    term_headers = sorted(terms)
    with io.StringIO() as output:
        output.write("<table class='grades'>")
        output.write("<tr>")
        for th in term_headers:
            output.write(f"<th>{th}</th>")
        output.write("</tr>")
        output.write("<tr>")
        for th in term_headers:
            if (th in course_by_term):
                g = course_by_term[th]
                output.write(f"<td><em>{g.teacher_name()}</em><br/>\n{g.print_term_grade()}</td>")
            else:
                output.write(f"<td></td>")
        output.write("</tr>")
        output.write("</table>")
        return output.getvalue()


def generate_comments_table(course_by_term, terms):
    term_headers = sorted(terms)
    with io.StringIO() as output:
        output.write("<table class='comments'>")
        output.write(f"<tr><th class='cbodyterm'>Term</th><th class='cbodytext'>Comments</th></tr>")
        for th in term_headers:
            output.write(f"<tr><td class='cbodyterm'>{th}</td>\n")
            if (th in course_by_term):
                g = course_by_term[th]
                if g.comments != None:
                    output.write(f"<td class='cbodytext'>{g.format_comments()}</td>")
                else:
                    output.write(f"<td class='cbodytext'></td>")

            else:
                output.write(f"<td class='cbodytext'></td>")
        output.write("</table>")
        return output.getvalue()


def collect_grades(root):
    all_grades = []
    all_years = []
    findall = root.findall(".//ns1:Term", ns)
    for term in findall:
        year = term[0][0].text
        if year not in all_years:
            all_years.append(year)
        for courses in term.iter("{http://www.sifinfo.org/infrastructure/2.x}Courses"):
            for course in courses:
                grade = process_course(course, year)
                all_grades.append(grade)

    return (all_grades, all_years)


def organize_by_term(grades):
    grade_list = sorted(grades, key=lambda gg: gg.term)
    grades_by_term = dict()
    for grade in grade_list:
        term = grade.term
        if term not in grades_by_term:
            grades_by_term[term] = []
        grades_by_term[term] = grade
    return grades_by_term


def organize_grades(all_grades):
    allCoursesByName = set()
    grades_by_course = dict()
    grades_by_period = dict()
    header_by_course = dict()

    for grade in all_grades:
        period = grade.reporting_period()
        allCoursesByName.add(grade.course_title)
        course_code = grade.course_code
        if course_code not in grades_by_course:
            grades_by_course[course_code] = []
        if period not in grades_by_period:
            grades_by_period[period] = []

        grades_by_period[period].append(grade)
        grades_by_course[course_code].append(grade)
        header_by_course[course_code] = grade.print_header()
    return (grades_by_course, grades_by_period, header_by_course)


def extractValidXML(inFile):
    with open(inFile, 'r') as f:
        return parse_file(f)


# concat all of the XML lines in the file, then return it
# Skip all up to the start of the XML
def parse_file(f):
    result = ''
    skip = True
    for line in f:
        if line.startswith('<?xml version="1.0" '):
            skip = False
        if not skip:
            # This is a known issue: last line being incomplete
            if (line.startswith('</StudentRec') and line != '</StudentRecordExchangeData>'):
                line = '</StudentRecordExchangeData>'
            result = result + line
    return result


def generate_html_file(file_name, body_text):
    css_text = ''
    with open('reportCard.css') as css_file:
        css_text = css_file.read()
    with  open(file_name, 'w') as f:
        f.write("<html>\n<head>\n")
        f.write(f"\n<style>{css_text}</style>\n")
        f.write("</head>\n<body>\n")
        f.write(body_text)
        f.write("\n</body>\n</html>")


if __name__ == "__main__":
    import sys

    parser = argparse.ArgumentParser(description='Report Card Generator.')
    parser.add_argument('--output_basename', action='store',
                        default='report_card',
                        help='Output file to report results to (default: standard out)')

    # First arg is the data file
    parser.add_argument('data_file')
    args = parser.parse_args()
    basename = args.output_basename
    print("output = ", basename)
    print("parsing ", args.data_file)

    valid_xml = extractValidXML(args.data_file)
    (student_info, grades, years) = process_data(valid_xml)
    years.sort()

    for year in years:
        (grades_by_course, grades_by_period, headers_by_course) = organize_grades(
            [a for a in grades if (a.year == year)])
        print("*******************", year, "***************")
        schools = [g.school for g in grades if (g.year == year)]
        terms = [g.term for g in grades if (g.year == year)]
        report_text = generate_year_report(student_info, year, grades_by_course, set(schools), set(terms))
        file_name = f"{basename}-{year}.html"
        generate_html_file(file_name, report_text)
