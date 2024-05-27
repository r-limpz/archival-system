from flask import Blueprint, request, render_template, jsonify
from flask_login import login_required, current_user
from flask import current_app as app
from werkzeug.utils import secure_filename
from PIL import Image
import base64
import json
import os
import io
from . import config 

uploader_manager = Blueprint('upload_manager', __name__,url_prefix='/archival')

class Colleges:
    def __init__(self, college_id, college_name, courses):
        self.college_id = college_id
        self.college_name = college_name
        self.courses = courses

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def convert_pic(filename):
    filename = ""
    with (filename,'rb').read() as file:
        photo = file.read
    return photo 

def getEditor():
    with config.conn.cursor() as cursor:
        cursor.execute('SELECT * FROM user WHERE username = %s', (current_user.username))
        account_uploader = cursor.fetchone()

        if account_uploader:
            editor = account_uploader['user_id']
            return editor
        else:
            return None
    
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
                        print(col_id,' : ', course_format['course_id'])
                # Create a new college object with fetched courses and append it to the list
                college = Colleges(col_id, col_name, courses)
                Col_Course_list.append(college)
                
        return Col_Course_list
    else:
        return None
    
def newDocumentUploader(document_header, imageFile):
    if document_header:
        document = document_header
        filename = document.get('filename')
        college = document.get('college')
        course = document.get('course')
        year_level = document.get('yearLevel')
        section = document.get('section')
        subject_name = document.get('subject_name')
        unit = document.get('subject_type')
        semester = document.get('semester')
        academic_year = document.get('academicYear')
        document_image = imageFile.read()

    if college != "" and course != "":
        try:
            with config.conn.cursor() as cursor:
                cursor.execute('SELECT * FROM documents WHERE filename = %s', (filename))
                document_exist = cursor.fetchone()

                if not document_exist:
                    editor = getEditor()
                    cursor.execute('INSERT INTO documents (filename, image_file, college, course, section, subject, academic_year, semester, year_level, unit, editor) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (filename, document_image, college, course, section, subject_name, academic_year, semester, year_level, unit, editor))
                    config.conn.commit()

                    document_id = cursor.lastrowid

                    if document_id:
                        return document_id
                    else:
                        return None
                else:
                    return None
        except Exception as e:
                print(f"Upload document error occurred: {e}")
                return e
    else:
        return None

def newStudent(entry_surname,entry_firstname, entry_middlename, entry_suffix):
    if not entry_surname and not entry_firstname:
        return None
    else:
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM students WHERE surname = %s AND firstname = %s AND middlename = %s AND suffix = %s', (entry_surname, entry_firstname, entry_middlename, entry_suffix) )
            student_credentials = cursor.fetchone()

            if not student_credentials:
                cursor.execute('INSERT INTO students(surname, firstname, middlename, suffix) VALUES (%s,%s,%s,%s)', (entry_surname, entry_firstname, entry_middlename, entry_suffix))
                config.conn.commit()
                return cursor.lastrowid
            else:
                return student_credentials['student_id']

def generateLink(document_id, student_id):
    if not document_id and not student_id :
        return None
    else:
        editor = getEditor()
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM tagging WHERE document = %s AND student = %s', (document_id, student_id))
            linked_item = cursor.fetchone()

            if not linked_item:
                cursor.execute('INSERT INTO tagging(document, student, editor) VALUES (%s,%s,%s)', (document_id, student_id, editor))
                config.conn.commit()

                return cursor.lastrowid
            else:
                return linked_item['tag_id']

def newRecordData(document_header, imageFile, students_data):
    document_id = newDocumentUploader(document_header, imageFile)
    try:
        with config.conn.cursor() as cursor:
            if students_data and document_id:
                tagging = []
                for student in students_data:
                    entry_surname = student['student_surname']
                    entry_firstname = student['student_firstname']
                    entry_middlename = student['student_middlename']
                    entry_suffix = student['student_suffixname']
                    student_id = newStudent(entry_surname,entry_firstname, entry_middlename, entry_suffix)

                    if student_id:
                        linked = generateLink(document_id, student_id)
                        tagging.append(linked)
                
                if len(tagging) > 0:
                    return'success'
                else:
                    return 'failed'
            else:
                return 'failed'  

    except Exception as e:
            print(f"new record error occurred: {e}")

@uploader_manager.route('/fetch_college/courseList/data', methods=['GET'])
@login_required
def display_colcourse():
    collegeCourses_list = fetch_course('all')
    return jsonify([college.__dict__ for college in collegeCourses_list])

@uploader_manager.route('/newRecord/document_upload', methods=['POST', 'GET'])
@login_required
def uploader():
    if 'document_image' not in request.files:
        return "No file uploaded"

    file = request.files['document_image']

    if file.filename == '' or not allowed_file(file.filename):
        return "Unsupported file type"

    # Extract other document information
    document_filename = request.form.get('document_filename')
    document_college = request.form.get('document_college')
    document_course = request.form.get('document_course')
    document_yearLevel = request.form.get('document_yearLevel')
    course_section = request.form.get('course_section')
    document_subject_name = request.form.get('document_subject_name')
    document_subject_type = request.form.get('document_subject_type')
    document_semester = request.form.get('document_semester')
    starting_year = request.form.get('starting_year')
    ending_year = request.form.get('ending_year')
    document_academicYear = f"{starting_year}-{ending_year}" if starting_year and ending_year else ''

    document_header = {
        'filename': document_filename,
        'college': int(document_college),
        'course': int(document_course),
        'yearLevel': int(document_yearLevel),
        'section': course_section,
        'subject_name': document_subject_name,
        'subject_type': int(document_subject_type),
        'semester': int(document_semester),
        'academicYear': document_academicYear,
    }

    students_data_str = request.form.get('studentsData')

    try:
        students_data = json.loads(students_data_str)
    except json.JSONDecodeError:
        students_data = []

    query_result = newRecordData(document_header, file, students_data)

    return jsonify({'query_result': query_result})

@uploader_manager.route('/displayImage/<document_id>', methods=['POST', 'GET'])
@login_required
def display_uploaded_image(document_id):
    with config.conn.cursor() as cursor:
        cursor.execute('SELECT * FROM documents WHERE docs_id = %s', (document_id,))
        document_data = cursor.fetchone()

        if document_data:
            document_image = document_data['image_file']
            encoded_image = base64.b64encode(document_image).decode('utf-8')
            return render_template('users/result.html', image=encoded_image)





