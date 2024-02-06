class Student:
    def __init__(self, given_name, middle_name, family_name):
        self.given_name = given_name
        self.middle_name = middle_name
        self.family_name = family_name

    @property
    def display_name(self):
        return "{0.given_name} {0.middle_name} {0.family_name}".format(self)


class Teacher:
    def __init__(self, given_name, family_name, school):
        self.given_name = given_name
        self.family_name = family_name
        self.school = school

    @property
    def display_name(self):
        return "{0.given_name} {0.family_name}".format(self)


class MarkingPeriod:
    def __init__(self, course, grade, percent, days_absent, comments):
        self.course = course
        self.grade = grade
        self.percent = percent
        self.days_absent = days_absent
        self.comments = comments

    def __str__(self):
        return "{0.course.course_title} - {0.course.period} - {0.grade} - {0.days_absent} - {0.comments}".format(self)

    @property
    def display_comments(self):
        if self.comments == None:
            return "-"
        else:
            return self.comments

class Term:
    def __init__(self, year):
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
        self.number_grade = number_grade
        self.percent = number_grade
        self.comments = comments

    def __str__(self):
        return "{} {} {}".format(self.letter_grade, self.number_grade, self.display_comments)
    @property
    def display_comments(self):
        if self.comments == None:
            return "-"
        else:
            return self.comments




class Grade:
    def __init__(self, course, term, grade_details):
        self.course = course
        self.term = term
        self.grade_details = grade_details

    def __str__(self) -> str:
        return f"{self.term.year}-{self.course.period} (code: {self.course.course_code}) {self.course.course_title} {self.grade_details.letter_grade}, {self.grade_details.number_grade}, {self.grade_details.comments}, {self.course.teacher.display_name()},  {self.course.teacher.school}"

    def format_comments(self):
        if (self.grade_details.comments != None):
            return self.grade_detailscomments.replace('\n', ' ')
        else:
            return ''


class Grades:
    def __init__(self, student, terms):
        self.student = student
        self.terms = terms
