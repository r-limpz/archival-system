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
def fetch_collegeList(search_college):
    if search_college:
        with config.conn.cursor() as cursor:
            #fetchall colleges in the database
            if search_college == 'all':
                cursor.execute('SELECT college_id, college_name FROM college WHERE 1=1')
                college_data = cursor.fetchall()
            else:
                college_id = int(search_college)
                cursor.execute('SELECT college_id, college_name FROM college WHERE college_id = %s', (college_id))
                college_data = cursor.fetchall()
            
            if college_data:
                return college_data
            else:
                return None
    else:
        return None
        
# function fetches the courses for each college and prepares the data for display
def fetch_course(search):
    college_list = fetch_collegeList(search) #utilize the fetch colleges function
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
def createCollege(college_name):
    if college_name:
        try:
            with config.conn.cursor() as cursor:
                cursor.execute('SELECT * FROM college WHERE college_name = %s', (college_name))
                collegeExist = cursor.fetchone()

                if not collegeExist:
                    cursor.execute('INSERT INTO college (college_name) VALUES (%s)', (college_name))
                    config.conn.commit()

                    cursor.execute('SELECT * FROM college WHERE college_name = %s', (college_name))
                    query = cursor.fetchone()

                    if query:
                        return 'success'
                    else:
                        return 'failed'
                else:
                    return 'duplicate'
        except Exception as e:
            print(f"Add college error occurred: {e}")
    else:
        return 'failed'

#add course function
def createCourse(addon_College, newcourse_name):
    if newcourse_name:
        try:
            with config.conn.cursor() as cursor:
                cursor.execute('SELECT * FROM courses WHERE course_name = %s', (newcourse_name))
                course_exist = cursor.fetchone()

                college_id = int(addon_College)

                if not course_exist:
                    cursor.execute('INSERT INTO courses (course_name, registered_college) VALUES (%s, %s)', (newcourse_name, college_id))
                    config.conn.commit()

                    cursor.execute('SELECT * FROM courses WHERE course_name = %s', (newcourse_name))
                    success = cursor.fetchone()
                    print('nigga2')
                    print(success)
                    if success:
                        return 'success'
                    else:
                        return 'failed'
                else:
                    return 'duplicate'
                
        except Exception as e:
            print(f"Add Courses error occurred: {e}")
    else:
        return 'failed'

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
@college_manager.route('/display_colleges' , methods=['GET'])
@login_required
@admin_required
def display_colcourse():
    collegeCourses_list = fetch_course('all')
    #each entry in the collgeCourses_list is collgeCourses_list[{college_id:'', college_name:'' courses[{1, course_id:'course_id',course_name:'course_name',}]}]
    return jsonify([college.__dict__ for college in collegeCourses_list])

@college_manager.route('/add/new_college', methods=['POST', 'GET'])
@login_required
@admin_required
def create_college():
    if request.method == "POST":
        newcollege_name = request.form.get('newcollege_name')
        query_result = createCollege(newcollege_name)

        if query_result:
            return jsonify({'query_result' : query_result})
        else:
            return jsonify({'query_result' : 'failed'})

@college_manager.route('/add/new_course' , methods=['POST', 'GET'])
def create_courses():
    if request.method == "POST":
        addon_College = request.form.get('addon_College')
        newcourse_name = request.form.get('newcourse_name')

        query_result = createCourse(addon_College, newcourse_name)

        if query_result:
            return jsonify({'query_result' : query_result})
        else:
            return jsonify({'query_result' : 'failed'})