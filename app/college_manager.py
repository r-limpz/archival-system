from flask import Blueprint, request, redirect, render_template, jsonify, url_for, abort
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

#setup the college object class for storing the college information
class Colleges:
    def __init__(self, college_id, college_name, courses):
        self.college_id = college_id
        self.college_name = college_name
        self.courses = courses

#fetch a list of colleges in the database and return the values as list
def fetch_collegeList():
    with config.conn.cursor() as cursor:
        #fetchall colleges in the database
        cursor.execute('SELECT college_id, college_name FROM college WHERE 1=1')
        college_data = cursor.fetchall()

        if college_data:
            return college_data
        else:#return none to prevent errors
            return None
        
#fetch the courses and finalize the data for displaying in the page
def fetch_course():
    college_list = fetch_collegeList() #utilize the fetch colleges function
    Col_Course_list = [] #list to store this data 
    #check if the college list is not empty to prevent errors to occured, cannot load Nonetype data
    if college_list:
        with config.conn.cursor() as cursor: 
            for college_item in college_list: #iterate the fetch colleges to search for courses 
                col_id = college_item.get('college_id') #setup variable to be used for search
                col_name = college_item.get('college_name')
                #execute a query for the search function of courses 
                cursor.execute('SELECT course_id, course_name FROM courses WHERE registered_college =%s', (col_id))
                course_item = cursor.fetchall()
                courses = [] #temporary array storing courses data for each college
                
                if course_item: #if has college data fetched
                    for entry in course_item: #iterate the fetched list of courses to append to a dictionary
                        course_format = {'course_id' :"", 'course_name':""} #setup temporary dictionary storing course data 
                        course_format['course_id'] = entry['course_id']
                        course_format['course_name'] = entry['course_name']
                        courses.append(course_format) #append the dictionary in the list

                college = Colleges(col_id, col_name, courses) #setup new entry of a college with a list of courses 
                Col_Course_list.append(college) # append this to the list 
                #each entry in the collgeCourses_list is collgeCourses_list[{college_id:'', college_name:'' courses[{1, course_id:'course_id',course_name:'course_name',}]}]
        return Col_Course_list
    else:
        return None

#A display route to return all data from fetched colleges
@college_manager.route('/display_colleges')
def display_colcourse():
    collegeCourses_list = fetch_course()
    #using the college classname to convert the list as readable object data to json
    return jsonify([college.__dict__ for college in collegeCourses_list])
