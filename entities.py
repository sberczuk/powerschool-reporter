

class Student:
    def __init__(self,given_name,  middle_name, family_name):
        self.given_name = given_name
        self.middle_name = middle_name
        self.family_name = family_name

    def display_name(self):
        return "{0.given_name} {0.middle_name} {0.family_name}".format(self)

class Teacher:
    def __init__(self,  given_name, family_name, school):
        self.given_name = given_name
        self.family_name = family_name
        self.school = school

    def display_name(self):
        return "{0.given_name} {0.family_name}".format(self)

class MarkingPeriod:
    def __init__(self, course,grade, percent,  days_absent, comments):

        self.course = course
        self.grade = grade
        self.percent = percent
        self.days_absent = days_absent
        self.comments = comments

class Term:
    def __init__(self,year):
        self.year = year
        self.grades = []

class Course:
    def __init__(self, school_year, grade_level, period, course_code, course_title, teacher):
        self.school_year = school_year
        self.grade_level = grade_level
        self.period = period
        self.course_code = course_code
        self.course_title = course_title
        self.teacher = teacher


class GradeDetails:
    def __init__(self, letter_grade, number_grade, comments):
        self.letter_grade = letter_grade
        self.number_grade =number_grade
        self.comments = comments
class Grade:
    def __init__(self, course, grade_details):
        self.course = course
        self.grade_details = grade_details
class Grades:
    def __init__(self, student, terms):
        self.student = student
        self.terms = terms




