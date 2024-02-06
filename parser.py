#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import argparse

from entities import Student, Course, Teacher, Grade, MarkingPeriod, Grades, Term

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
    days_absent = course_node.find(".//ns1:DaysAbsent", ns).text

    # details = GradeDetails(letter_grade,number_grade, comments)
    details = MarkingPeriod(course, letter_grade, number_grade, days_absent, comments)
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


def organize_by_term(grades):
    grade_list = sorted(grades, key=lambda gg: gg.term)
    grades_by_term = dict()
    for grade in grade_list:
        term = grade.term
        if term not in grades_by_term:
            grades_by_term[term] = []
        grades_by_term[term] = grade
    return grades_by_term


def extractValidXML(inFile):
    '''open the  data file and delegate to the parser function'''
    with open(inFile, 'r') as f:
        return parse_file(f)



def parse_file(f):
    '''parse a powerschool file, correcting for error in the closing element'''
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
    '''generate  an html file  with the specified name injecting body_text into the body element'''
    css_text = ''
    with open('reportCard.css') as css_file:
        css_text = css_file.read()
    with  open(file_name, 'w') as f:
        f.write("<html>\n<head>\n")
        f.write(f"\n<style>{css_text}</style>\n")
        f.write("</head>\n<body>\n")
        f.write(body_text)
        f.write("\n</body>\n</html>")


def generate_report(grades):
    student_name = grades.student.display_name
    sorted_terms = sorted(grades.terms, key=lambda t: t.year)
    grades_by_year = {}
    for t in sorted_terms:
        grades_by_year[t.year] = grades_by_year.get(t.year, [])
        grades_by_year[t.year].extend(t.grades)
    # group terms by year
    for y in grades_by_year.keys():
        ts = grades_by_year.get(y)
        print("*******************", y, student_name, "***************")

        year = y

        grade_map_for_year = {}
        for g in ts:
            # todo: is this idiomatic?
            grade_map_for_year[g.course.course_title] = grade_map_for_year.get(g.course.course_title, [])
            grade_map_for_year[g.course.course_title].append(g)

        file_name = f"{basename}-{year}.html"

        #  below   returns a string?
        report_text = generate_year_report(grades.student, year, grade_map_for_year)
        generate_html_file(file_name, report_text)
        print("generated  file file://{0}".format(file_name))


def get_grade_html(grade_details):
    period = grade_details.course.period.lower()
    s = """
    <div class='{1}'>{0.course.period}</div>
     <div class='grade-{1}'>{0.grade}</div> 
     <div class='absent-{1}'> days absent {0.days_absent}</div>
    <div class='comments-{1}'>{0.display_comments}</div>""".format(grade_details, period)

    return s


def generate_year_report(student, year, grade_map_for_year):
    report_text = "<h1>{0.display_name} - {1}</h1>".format(student, year)
    print("YEAR REPORT ", year)
    for s in grade_map_for_year.keys():
        term_grades_for_subject = grade_map_for_year.get(s)
        # get  list of unique subjects for this year
        courses_for_term = set([g.course.course_title for g in term_grades_for_subject])
        # filter for courses in this term
        course_grades_for_term = [g for g in term_grades_for_subject if g.course.course_title in courses_for_term]
        #  collect the grades for each course
        subject_grades = [g for g in course_grades_for_term if g.course.course_title == s]
        subject_grades.sort(key=lambda t: t.grade_details.course.period)
        html = get_term_subject_grade_html(s, subject_grades)
        report_text += html
    return report_text


def get_term_subject_grade_html(subject, subject_grades):
    s = """<div class='grid-container'><div class='course-title'>{0}</div>""".format(subject)
    for gg in subject_grades:
        s += get_grade_html(gg.grade_details)
    s += "</div>"
    return s


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
    # group grades by course code?
    # for each term we want a map of course info -> grade
    generate_report(grades)
