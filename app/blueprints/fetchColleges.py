from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.college.college_selector import fetch_course
from app.secure.authorization import authenticate

fetchColleges = Blueprint('fetchCollege_data', __name__)

class Colleges:
    def __init__(self, college_id, college_name, college_description, courses):
        self.college_id = college_id
        self.college_name = college_name
        self.college_description = college_description
        self.courses = courses

@fetchColleges.route('/fetch_college/courseList/data', methods=['GET'])
@login_required
@authenticate
def display_colcourse():
    if current_user.is_authenticated and (current_user.role == 'admin' or current_user.role == 'staff') and current_user.is_active:
        collegeCourses_list = fetch_course('all')
        if collegeCourses_list:
            return jsonify([college.__dict__ for college in collegeCourses_list])