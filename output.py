import io
import string

from parser import organize_by_term




grade_template = """<div class='course-title'>{0.course.course_title}</div>
<div class='course-period'>{0.course.period}</div>
<div class='letter-grade'>{0.grade_details.letter_grade}</div>
<div class='teacher-name'>{0.course.teacher.display_name}</div>
<div class='period-comments'>{0.grade_details.display_comments}</div>
"""
def format_grade(t):
    return  grade_template.format(t)
    # string.Template(templ).substitute(t)
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
