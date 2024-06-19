from flask import Blueprint, request, jsonify, Response, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
import base64
from . import config

fetch_documents = Blueprint('fetch_documents', __name__, url_prefix='/documents/manage')

#decorator for authorization role based
def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated and not current_user.is_active and current_user.role not in ['admin', 'staff']:
                return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def getEditor():
    with config.conn.cursor() as cursor:
        cursor.execute('SELECT * FROM user WHERE username = %s', (current_user.username))
        account_uploader = cursor.fetchone()

        if account_uploader:
            editor = account_uploader['user_id']
            return editor
        else:
            return None

def filesize_format(filesize):
    if filesize >= 1024 * 1024 * 1024:  # Greater than or equal to 1 GB
        formatted_size = f"{filesize / (1024 * 1024 * 1024):.2f} GB"
    elif filesize >= 1024 * 1024:  # Greater than or equal to 1 MB
        formatted_size = f"{filesize / (1024 * 1024):.2f} MB"
    else:
        formatted_size = f"{filesize / 1024:.2f} KB"
    
    return formatted_size

def fetchDocumentData(document_id):
    try:
        with config.conn.cursor() as cursor:
            
            if document_id:
                cursor.execute('SELECT * FROM documents WHERE docs_id = %s', (document_id))
                document = cursor.fetchone()

                document_header = {
                    'filename': document['filename'],
                    'college': document['college'],
                    'course': document['course'],
                    'year_level': document['year_level'],
                    'section': document['section'],
                    'subject':document['subject'],
                    'unit': document['unit'],
                    'semester': document['semester'],
                    'academic_year': document['academic_year'],
                }
        
                return document_header
    except Exception as e:
        print('Fetch Document Info Error :', e)

def editDocumentsData(document_id, document_header):
    try:
        with config.conn.cursor() as cursor:
            if document_id:
                document_id = int(document_id)
                document = document_header
                new_filename = document.get('filename')
                new_college = document.get('college')
                new_course = document.get('course')
                new_year_level = document.get('yearLevel')
                new_section = document.get('section')
                new_subject_name = document.get('subject_name')
                new_unit = document.get('document_unit')
                new_semester = document.get('semester')
                new_academic_year = document.get('academicYear')

                cursor.execute('UPDATE documents SET filename = %s, college = %s, course = %s, section = %s, subject = %s, academic_year = %s, semester = %s, unit = %s, year_level = %s WHERE docs_id = %s', 
                               (new_filename, new_college, new_course, new_section, new_subject_name, new_academic_year, new_semester, new_unit, new_year_level, document_id))
                config.conn.commit()  # Commit the changes!

                if cursor.rowcount > 0:
                    return 'success'
                            
                return 'failed'

            return 'No Selected Document'
    except Exception as e:
        print('Edit Documents Error:', e)

def deleteDocumentsData(document_id):
    try:
        with config.conn.cursor() as cursor:
            if document_id:
                editor = getEditor()

                cursor.execute('UPDATE documents SET delete_status = 1 WHERE docs_id = %s', (document_id,)) 
                config.conn.commit()

                if cursor.rowcount > 0:
                    cursor.execute('INSERT INTO trashdocs (document_id, editor, trashed_date, deleted_date) VALUES (%s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 30 DAY))', (document_id, editor))
                    config.conn.commit()

                    return 'success'
                            
            return 'failed'
    except Exception as e:
        print('Delete Documents Error:', e)

#fetch data for datatable
@fetch_documents.route("/data/fetch/",methods=["POST","GET"])
@login_required
@authenticate
def documents_data():
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
                    search_query += f" and (Filename like '%{term}%' or College like '%{term}%' or Course like '%{term}%' or Subject like '%{term}%' or SchoolYear like '%{term}%' or Semester like '%{term}%' or Unit like '%{term}%') "
            
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
                cursor.execute("SELECT count(*) as allcount from documentstbl")
                records = cursor.fetchone()
                total_records = records['allcount']

                # Total number of records with filtering
                cursor.execute(f"SELECT count(*) as allcount from documentstbl WHERE 1 {search_query}")
                records = cursor.fetchone()
                total_record_with_filter = records['allcount']

                # Fetch records
                if rowperpage == -1:  # If length is -1, then it's "All"
                    stud_query = f"SELECT * FROM documentstbl WHERE 1 {search_query} ORDER BY {column_name} {column_sort_order}"
                    cursor.execute(stud_query)
                    recordlist = cursor.fetchall()
                # limite records
                else:
                    stud_query = f"SELECT * FROM documentstbl WHERE 1 {search_query} ORDER BY {column_name} {column_sort_order} LIMIT {row},{rowperpage}"
                    cursor.execute(stud_query)
                    recordlist = cursor.fetchall()

                data = []
                if recordlist:
                    if current_user.role == 'staff':
                        for row in recordlist:
                            data.append({
                                'id': row['id'],
                                'Filename': row['Filename'],
                                'College': row['College'],
                                'Section': row['Course'] + '-' +  row['Section'],
                                'Subject': row['Subject'],
                                'Unit': row['Unit'],
                                'Semester': row['Semester'],
                                'SchoolYear': row['SchoolYear'],
                                'image_id': row['image_id'],
                                'Uploader': '',
                            })
                
                    if current_user.role == 'admin':
                        for row in recordlist:
                            data.append({
                                'id': row['id'],
                                'Filename': row['Filename'],
                                'College': row['College'],
                                'Section': row['Course'] + '-' +  row['Section'],
                                'Subject': row['Subject'],
                                'Unit': row['Unit'],
                                'Semester': row['Semester'],
                                'SchoolYear': row['SchoolYear'],
                                'image_id': row['image_id'],
                                'File_size':filesize_format(row['Filesize']) ,
                                'Uploader': row['Uploader'],
                            })
                    
                response = {
                    'draw': draw,
                    'iTotalRecords': total_records,
                    'iTotalDisplayRecords': total_record_with_filter,
                    'aaData': data,
                }

                return jsonify(response)
    except Exception as e:
        print('Fetch documents Error: ',e)

#preview document image
@fetch_documents.route('/data/file/fetch_data/<image_id>', methods=['POST', 'GET'])
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

#fetch document info
@fetch_documents.route('/data/document_header/request/data/<document_id>', methods=['POST', 'GET'])
@login_required
@authenticate
def getEntryData(document_id):
    document_id = int(document_id)

    if document_id:
        query_result = fetchDocumentData(document_id)
        return jsonify(query_result)
    
#update document info
@fetch_documents.route('/data/document_header/update', methods=['POST', 'GET'])
@login_required
@authenticate
def editDocument():

    if request.method == "POST":
        document_id = request.form.get('document_id')
        update_filename = request.form.get('update_filename')
        update_college = request.form.get('update_college')
        update_course = request.form.get('update_course')
        update_year_level = request.form.get('update_year_level')
        update_section = request.form.get('update_section')
        update_semester = request.form.get('update_semester')
        update_subject = request.form.get('update_subject')
        update_unit = request.form.get('update_unit')
        update_academicYear = request.form.get('update_academicYear')
        

        document_header = {
            'filename': update_filename,
            'college': int(update_college),
            'course': int(update_course),
            'yearLevel': int(update_year_level),
            'section': update_section,
            'subject_name': update_subject,
            'document_unit': int(update_unit),
            'semester': int(update_semester),
            'academicYear': update_academicYear,
        }
        
        update_query = editDocumentsData(document_id, document_header)

        if update_query:
            return jsonify({'update_query': update_query})

#delete document temporary
@fetch_documents.route('/data/file/delete', methods=['POST', 'GET'])
@login_required
@authenticate
def deleteDocument():

     if request.method == "POST":
        document_id = request.form.get('document_id')
        document_id = int(document_id)

        delete_query = deleteDocumentsData(document_id)

        if delete_query:
            return jsonify({'delete_query': delete_query})