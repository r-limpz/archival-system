from flask import Blueprint, request, jsonify, Response
from flask_login import login_required, current_user
import base64
import json
from . import config

data_fetch = Blueprint('data', __name__)

@data_fetch.route("/records_data",methods=["POST","GET"])
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
                    search_query += f" and (FullName like '%{term}%' or College like '%{term}%' or Course like '%{term}%' or Subject like '%{term}%' or SchoolYear like '%{term}%' or Semester like '%{term}%' or Section like '%{term}%') "
            
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
                            'Course': row['Course'],
                            'Section': row['Section'],
                            'Subject': row['Subject'],
                            'Unit': row['Unit'],
                            'Semester': row['Semester'],
                            'SchoolYear': row['SchoolYear'],
                            'image_id': row['image_id'],
                        })
                else:
                    print('NO RECORDS ')
                    
                response = {
                    'draw': draw,
                    'iTotalRecords': total_records,
                    'iTotalDisplayRecords': total_record_with_filter,
                    'aaData': data,
                }

                return jsonify(response)
    except Exception as e:
        print(e)

#preview document image
@data_fetch.route('/getDocImage/image/data/<image_id>', methods=['POST', 'GET'])
@login_required
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
