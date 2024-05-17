from flask import Blueprint, request, redirect, render_template, jsonify, url_for, abort
from flask_login import login_required, current_user
from functools import wraps
from flask import current_app as app
from . import config 

college_manager = Blueprint('college_manager', __name__,url_prefix='/admin/college_manager')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated and current_user.role != 'admin' or not current_user.is_active:
            return redirect(url_for('home'))
        elif current_user.is_authenticated and current_user.is_active and current_user.role == 'staff':
            return redirect(url_for('staff.records'))
        return f(*args, **kwargs)
    return decorated_function

class College:
    def __init__(self, college_id, college_name, courses):
        self.college_id = college_id
        self.college_name = college_name
        self.courses = courses

def fetch_collegeList():
    with config.conn.cursor() as cursor:
        cursor.execute('SELECT college_id, college_name FROM college WHERE 1=1')
        college_data = cursor.fetchall()

        if college_data:
            return college_data
        else:
            return None 

def fetch_course():
    college_list = fetch_collegeList()
    Col_Course_list = []

    with config.conn.cursor() as cursor: 
        for college_item in college_list:
            col_id = college_item.get('college_id')
            col_name = college_item.get('college_name')

            cursor.execute('SELECT course_id, course_name FROM courses WHERE registered_college =%s', (col_id))
            course_item = cursor.fetchall()
            courses = []
            
            if course_item:
                for entry in course_item:
                    course_format = {'course_id' :"", 'course_name':""}
                    course_format['course_id'] = entry['course_id']
                    course_format['course_name'] = entry['course_name']
                    courses.append(course_format)

            college = College(col_id, col_name, courses)
            Col_Course_list.append(college)

    return Col_Course_list

@college_manager.route('/display_colleges')
def display_colcourse():
    collegeCourses_list = fetch_course()
    #each entry in the collgeCourses_list is collgeCourses_list[{college_id:'', college_name:'' courses[{1, course_id:'course_id',course_name:'course_name',}]}]
    return jsonify([college.__dict__ for college in collegeCourses_list])
