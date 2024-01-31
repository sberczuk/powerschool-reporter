#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import argparse

from entities import Student, Course, Teacher, Grade, GradeDetails, Grades,Term

ns = {'ns1': 'http://www.sifinfo.org/infrastructure/2.x',
      'ns2': 'http://stumo.transcriptcenter.com'}






# Placeholder for markdown format for a list of grades
# Take the list and sort it with appropriate headers.
# TBD if we need to figure pass in meta data, whether we figure it out, or if we make assumptions.
def format_as_markdown(grades):
    pass


def process_data(xml_string):
    """Process all the data iin the XML file"""
    root = ET.fromstring(xml_string)
    student = parse_element(root, '{0}:StudentDemographicRecord'.format("ns1"), parse_student)
    terms = parse_element(root, '{0}:StudentAcademicRecord/{0}:CourseHistory'.format('ns1'), parse_terms)

    return Grades(student, terms)


def parse_element(root, path, function):
    """given an xpath to an element, find it, and apply function to it"""
    node = root.find(path, namespaces=ns)
    entity = function(node)
    return entity


def parse_student(root):
    """parse the element with student data and return  a Student object"""
    ns_name = '{0}StudentPersonalData/{0}Name'.format('ns1:')
    name = root.find(ns_name, namespaces=ns)
    fn = name.find("ns1:FirstName", namespaces=ns).text
    mi = name.find("ns1:MiddleName", namespaces=ns).text
    ln = name.find("ns1:LastName", namespaces=ns).text
    return Student(fn, mi, ln)


def process_course(course_node, term, year):
    """Process an  individual course element"""
    extended_info = course_node.find("ns1:SIF_ExtendedElements", ns)
    term_id = extended_info.find("ns1:SIF_ExtendedElement[@Name='StoreCode']", ns).text
    teacher_fn = extended_info.find("ns1:SIF_ExtendedElement[@Name='InstructorFirstName']", ns).text
    teacher_ln = extended_info.find("ns1:SIF_ExtendedElement[@Name='InstructorLastName']", ns).text
    school_name = extended_info.find("ns1:SIF_ExtendedElement[@Name='SchoolName']", ns).text
    teacher = Teacher(teacher_fn, teacher_ln, school_name)

    course_title = course_node.find(".//ns1:CourseTitle", ns).text
    course_code = course_node.find(".//ns1:CourseCode", ns).text
    grade_level = course_node.find(".//ns1:GradeLevelWhenTaken/ns1:Code", ns).text
    course = Course(year, grade_level, term_id, course_code, course_title, teacher)

    mark_data = course_node.find(".//ns1:MarkData", ns)
    letter_grade = mark_data.find("ns1:Letter", ns).text
    number_grade = mark_data.find("ns1:Percentage", ns).text
    comments = mark_data.find("ns1:Narrative", ns).text

    details = GradeDetails(letter_grade,number_grade, comments)

    return Grade(course, term, details)


def parse_terms(root):
    """parse the sub elements of Course History, which has the grade info. Returns
    a list of Grade objects"""
    # Path  from StudentAcademicRecord/CourseHistory
    terms = []
    term_nodes = root.findall("{0}Term".format("ns1:"), ns)
    for term_node in term_nodes:
        school_year = term_node.find("{0}TermInfoData/{0}SchoolYear".format("ns1:"), ns).text

        term = Term(school_year)
        courses_node = term_node.find("{0}Courses".format("ns1:"), ns)
        grades = []
        for c in courses_node.findall("{0}:Course".format("ns1"), ns):
            grades.append(process_course(c, term, school_year))
        term.grades = grades
        terms.append(term)
    return terms


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
                grade = process_course(course, term, year)
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


def generate_text(grades, year):
    pass


def generate_report(grades):
    student_name = grades.student.display_name()
    for t in grades.terms:
        year = t.year
        file_name = f"{basename}-{year}.html"
        print("*******************", year, student_name, "***************")
        report_text = ""
        for g in t.grades:
            print(g)
            #generate_text(grades, year))
        generate_html_file(file_name, report_text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Report Card Generator.')

    parser.add_argument('--output_basename', action='store',
                        default='report_card',
                        help='Output file to report results to (default: standard out)')

    # First arg is the data file
    parser.add_argument('data_file')
    args = parser.parse_args()
    basename = args.output_basename

    parser.add_argument('data_file')
    print("output = ", basename)
    print("parsing ", args.data_file)

    valid_xml = extractValidXML(args.data_file)
    grades = process_data(valid_xml)

    # collect all the years
    generate_report(grades)
