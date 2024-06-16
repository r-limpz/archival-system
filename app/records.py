from flask import Blueprint, request, jsonify, Response, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
import base64
import json
from . import config

fetch_records = Blueprint('fetch_records', __name__, url_prefix='/documents/records/tags/manage/data')

#decorator for authorization role based
def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated and not current_user.is_active and current_user.role not in ['admin', 'staff']:
                return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


def fetchEntryData(tag_id):
    try:
        with config.conn.cursor() as cursor:
            cursor.execute(""" SELECT students.*, tagging.* FROM students JOIN tagging ON students.student_id = tagging.student WHERE tagging.tag_id = %s """, (tag_id,))
            student_data = cursor.fetchone()

            record_data = { 'surname': '', 'firstname': '', 'middlename': '', 'suffix': '' }

            record_data['surname'] = student_data['surname']
            record_data['firstname'] = student_data['firstname']
            record_data['middlename'] = student_data['middlename']
            record_data['suffix'] = student_data['suffix']

            return record_data

    except Exception as e:
        print('Fetch Recordds Error :', e)

def editRecordsData(tagging_id, new_surname, new_firstname, new_middlename, new_suffix):
    try:
        with config.conn.cursor() as cursor:
            tagging_id = int(tagging_id)
            cursor.execute(""" SELECT students.*, tagging.* FROM students JOIN tagging ON students.student_id = tagging.student WHERE tagging.tag_id = %s """, (tagging_id,))
            studentData = cursor.fetchone()

            if studentData:
                if studentData['surname'] == new_surname and studentData['firstname'] == new_firstname and studentData['middlename'] == new_middlename and studentData['suffix'] == new_middlename:
                    return 'no changes'
                else:
                    cursor.execute(""" INSERT INTO students (surname, firstname, middlename, suffix) SELECT %s, %s, %s, %s WHERE NOT EXISTS 
                                  ( SELECT 1 FROM students WHERE surname = %s AND firstname = %s AND middlename = %s AND suffix = %s ) """,
                                    (new_surname, new_firstname, new_middlename, new_suffix, new_surname, new_firstname, new_middlename, new_suffix))
                   
                    cursor.execute('SELECT student_id FROM students WHERE surname = %s AND firstname = %s AND middlename = %s AND suffix = %s', (new_surname, new_firstname, new_middlename, new_suffix))
                    studentID = cursor.fetchone()['student_id']

                    if studentID:
                        cursor.execute('UPDATE tagging SET student = %s WHERE tag_id = %s', (studentID, tagging_id))
                        config.conn.commit()

                        if cursor.rowcount > 0:
                            return 'success'
                            
                        return 'failed'
                
            return 'entry not found'
    except Exception as e:
        print('Unlink Recordds Error :', e)

def removeRecordData(tagging_id):
    try:
        with config.conn.cursor() as cursor:
            tagging_id = int(tagging_id)

            cursor.execute('DELETE FROM tagging WHERE tag_id = %s', (tagging_id))
            rows_deleted = cursor.rowcount  # Get the number of affected rows

            config.conn.commit()

            if rows_deleted > 0:
                return 'success'
            
            return 'failed'
            
    except Exception as e:
        print('Remove Recordds Error :', e)

#fetch data for datatable
@fetch_records.route("/fetch/tags/students_list",methods=["POST","GET"])
@login_required
@authenticate
def records_data():
    try:
        if request.method == 'POST':
            draw = request.form.get('draw') 
            row = int(request.form.get('start'))
            rowperpage = int(request.form.get('length'))
            column_index = request.form.get('order[0][column]') # Column index
            column_name = request.form.get('columns['+column_index+'][data]') # Column name
            column_sort_order = request.form.get('order[0][dir]') # asc or desc

            filterSearch = request.form.get('filterSearch')
            filterCollege = request.form.get('filterCollege')
            filterCourse = request.form.get('filterCourse')
            filterSemester = request.form.get('filterSemester')
            filterYear = request.form.get('filterYear')

            search_query = ""

            if filterSearch:
                search_terms = filterSearch.split(' ')
                for term in search_terms:
                    search_query += f" and (FullName like '%{term}%' or College like '%{term}%' or Course like '%{term}%' or Subject like '%{term}%' or SchoolYear like '%{term}%' or Semester like '%{term}%' or Unit like '%{term}%') "
            
            if filterCollege:
                search_query += f" and (College = '{filterCollege}')"
            if filterCourse:
                search_query += f" and (Course = '{filterCourse}')"
            if filterYear:
                search_query += f" and (SchoolYear = '{filterYear}')"
            if filterSemester:
                search_query += f" and (Semester = '{filterSemester}')"  

            with config.conn.cursor() as cursor:
                # Total number of records without filtering
                cursor.execute("SELECT count(*) as allcount from srecordstbl")
                records = cursor.fetchone()
                total_records = records['allcount']

                # Total number of records with filtering
                cursor.execute(f"SELECT count(*) as allcount from srecordstbl WHERE 1 {search_query}")
                records = cursor.fetchone()
                total_record_with_filter = records['allcount']

                # Fetch records
                if rowperpage == -1:  # If length is -1, then it's "All"
                    stud_query = f"SELECT * FROM srecordstbl WHERE 1 {search_query} ORDER BY {column_name} {column_sort_order}"
                    cursor.execute(stud_query)
                    recordlist = cursor.fetchall()
                # limite records
                else:
                    stud_query = f"SELECT * FROM srecordstbl WHERE 1 {search_query} ORDER BY {column_name} {column_sort_order} LIMIT {row},{rowperpage}"
                    cursor.execute(stud_query)
                    recordlist = cursor.fetchall()

                data = []
                if recordlist:
                    for row in recordlist:
                        data.append({
                            'id': row['id'],
                            'FullName': row['FullName'],
                            'College': row['College'],
                            'Section': row['Course'] + '-' +  row['Section'],
                            'Subject': row['Subject'],
                            'Unit': row['Unit'],
                            'Semester': row['Semester'],
                            'SchoolYear': row['SchoolYear'],
                            'image_id': row['image_id'],
                        })
                    
                response = {
                    'draw': draw,
                    'iTotalRecords': total_records,
                    'iTotalDisplayRecords': total_record_with_filter,
                    'aaData': data,
                }

                return jsonify(response)
    except Exception as e:
        print('Fetch Records Error: ',e)

#preview document image
@fetch_records.route('/file/fetch_data/<image_id>', methods=['POST', 'GET'])
@login_required
@authenticate
def previewDocument(image_id):
    image_id = int(image_id)
    with config.conn.cursor() as cursor:
        cursor.execute('SELECT * FROM img_files WHERE img_id = %s', image_id)
        image_data = cursor.fetchone()

        if image_data:
            document_image = image_data['document_file']
            encoded_image = base64.b64encode(document_image).decode('utf-8')
            return Response(encoded_image)
        
        return "No image data found", 404
    
#fetch tag entry student credentials
@fetch_records.route('/students/request/credentials/<tag_id>', methods=['POST', 'GET'])
@login_required
@authenticate
def getEntryData(tag_id):
    tag_id = int(tag_id)

    if tag_id:
        query_result = fetchEntryData(tag_id)
        return jsonify(query_result)
    
#edit records data   
@fetch_records.route('/students/credentials/update', methods=['POST', 'GET'])
@login_required
@authenticate
def editEntryData():

    if request.method == "POST":
            tagging_id = request.form.get('tagging_id')
            new_surname = request.form.get('update_surname')
            new_firstname = request.form.get('update_firstname')
            new_middlename = request.form.get('update_middlename')
            new_suffix = request.form.get('update_suffix')

            tagging_id = int(tagging_id)

            if tagging_id:
                update_query = editRecordsData(tagging_id, new_surname, new_firstname, new_middlename, new_suffix)

                if update_query:
                    return jsonify({'update_query': update_query})
#delete records data                
@fetch_records.route('/students/remove/unlink/update/document', methods=['POST', 'GET'])
@login_required
@authenticate
def deleteEntryData():

    if request.method == "POST":
        tagging_id = request.form.get('tagging_id')
        tagging_id = int(tagging_id)

        delete_query = removeRecordData(tagging_id)

        if delete_query:
            return jsonify({'delete_query': delete_query})
        

