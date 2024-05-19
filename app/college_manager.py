from flask import Blueprint, request, redirect, jsonify, url_for
from flask_login import login_required, current_user
from functools import wraps
from flask import current_app as app
from . import config 

college_manager = Blueprint('college_manager', __name__,url_prefix='/admin/college_manager')

#decorator for authorization role based
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated and current_user.role != 'admin' or not current_user.is_active:
            return redirect(url_for('home'))
        elif current_user.is_authenticated and current_user.is_active and current_user.role == 'staff':
            return redirect(url_for('staff.records'))
        return f(*args, **kwargs)
    return decorated_function

#setup the college object class for the college information object
class Colleges:
    def __init__(self, college_id, college_name, courses):
        self.college_id = college_id
        self.college_name = college_name
        self.courses = courses

# function fetches a list of colleges from the database
def fetch_collegeList():
    with config.conn.cursor() as cursor:
        #fetchall colleges in the database
        cursor.execute('SELECT college_id, college_name FROM college WHERE 1=1')
        college_data = cursor.fetchall()

        if college_data:
            return college_data
        else:
            return None
        
# function fetches the courses for each college and prepares the data for display
def fetch_course():
    college_list = fetch_collegeList() #utilize the fetch colleges function
    Col_Course_list = [] #list to store this data

    # Proceed if college list is not empty
    if college_list:
        with config.conn.cursor() as cursor: 
            # Iterate over each college
            for college_item in college_list:
                col_id = college_item.get('college_id')
                col_name = college_item.get('college_name')
                
                # Execute SQL query to fetch courses for the current college
                cursor.execute('SELECT course_id, course_name FROM courses WHERE registered_college =%s', (col_id))
                course_item = cursor.fetchall()
                courses = [] #temporary array storing courses data for each college

                # If courses data exists, format and store it
                if course_item: 
                    # Iterate the fetched list of courses
                    for entry in course_item:
                        #setup temporary dictionary storing course data
                        course_format = {'course_id' :"", 'course_name':""}  
                        course_format['course_id'] = entry['course_id']
                        course_format['course_name'] = entry['course_name']
                        #append the dictionary in the list
                        courses.append(course_format) 
                        
                # Create a new college object with fetched courses and append it to the list
                college = Colleges(col_id, col_name, courses)
                Col_Course_list.append(college)
                
        return Col_Course_list
    else:
        return None

#add college function
def createCollege(college_name, college_abbrevation):
    pass

#add course function
def createCourse(course_name):
    pass

#update college function
def updateCollege(course_id, newCourse_name):
    pass

#update course function
def updateCourse(college_id, newCollege_name):
    pass

#remove college function
def removeCollege(college_id):
    pass

#remove course function
def removeCollege(college_id):
    pass

#A display route to return all data from fetched colleges
@college_manager.route('/display_colleges')
def display_colcourse():
    collegeCourses_list = fetch_course()
    #each entry in the collgeCourses_list is collgeCourses_list[{college_id:'', college_name:'' courses[{1, course_id:'course_id',course_name:'course_name',}]}]
    return jsonify([college.__dict__ for college in collegeCourses_list])
