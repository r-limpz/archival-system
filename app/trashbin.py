from flask import Blueprint, request, jsonify, Response, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
import base64
import json
from . import config

trashbin_data = Blueprint('trashbin', __name__, url_prefix='/admin/trash/manage/data/')

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

def get_deletionTime(delete_sched):
    if delete_sched:
        now = datetime.now().date() 
        diff = delete_sched - now  # Calculate the difference between the future date and now
        
        # If the difference is negative, it means the deletion time has passed
        if diff.days < 0:
            return "Deletion time has passed."
        
        # Format the time difference as a string indicating days left
        if diff.days > 0:
            time_str = f"{diff.days} days left" 
            return time_str
    else:
        return "Deletion schedule not provided."
    
def restoreDocumentFile(document_id):
    try:
        with config.conn.cursor() as cursor:

            cursor.execute('UPDATE documents SET delete_status = 0 WHERE docs_id = %s', (document_id,)) 
            config.conn.commit()

            if cursor.rowcount > 0:
                    cursor.execute('DELETE FROM trashdocs WHERE document_id = %s', (document_id))
                    config.conn.commit()

                    return 'success'

            return 'failed'
    except Exception as e:
            print('Recover data Error: ',e)

def deleteDocumentFile(document_id):
    try:
        with config.conn.cursor() as cursor:

            cursor.execute('DELETE FROM documents WHERE docs_id = %s', (document_id,)) 
            rows_deleted = cursor.rowcount  # Get the number of affected rows
            config.conn.commit()

            if rows_deleted > 0:
                    cursor.execute('DELETE FROM trashdocs WHERE document_id = %s', (document_id))
                    config.conn.commit()

                    return 'success'

            return 'failed'
        
    except Exception as e:
            print('Recover data Error: ',e)


@trashbin_data.route("/fetch-data/deleted-files/delete-schedule-30days/trash-list",methods=["POST","GET"])
@login_required
@admin_required
def recycleBin():
    try:
        if request.method == 'POST':
            draw = request.form.get('draw') 
            row = int(request.form.get('start'))
            rowperpage = int(request.form.get('length'))
            column_index = request.form.get('order[0][column]') # Column index
            column_name = request.form.get('columns['+column_index+'][data]') # Column name
            column_sort_order = request.form.get('order[0][dir]') # asc or desc

            filterSearch = request.form.get('filterSearch')
            
            search_query = ""

            if filterSearch:
                search_terms = filterSearch.split(' ')
                for term in search_terms:
                    search_query += f" and (Filename like '%{term}%') "

            with config.conn.cursor() as cursor:
                # Total number of records without filtering
                cursor.execute("SELECT count(*) as allcount from trashtbl")
                records = cursor.fetchone()
                total_records = records['allcount']

                # Total number of records with filtering
                cursor.execute(f"SELECT count(*) as allcount from trashtbl WHERE 1 {search_query}")
                records = cursor.fetchone()
                total_record_with_filter = records['allcount']

                # Fetch records
                if rowperpage == -1:  # If length is -1, then it's "All"
                    stud_query = f"SELECT * FROM trashtbl WHERE 1 {search_query} ORDER BY {column_name} {column_sort_order}"
                    cursor.execute(stud_query)
                    recordlist = cursor.fetchall()
                # limite records
                else:
                    stud_query = f"SELECT * FROM trashtbl WHERE 1 {search_query} ORDER BY {column_name} {column_sort_order} LIMIT {row},{rowperpage}"
                    cursor.execute(stud_query)
                    recordlist = cursor.fetchall()

                data = []
                if recordlist:
                    for row in recordlist:
                        
                        data.append({
                            'id': row['id'],
                            'Filename': row['Filename'],
                            'Trashed': row['Trash_date'].strftime('%B %d, %Y'),
                            'deletedOn': get_deletionTime(row['Deletion_Sched']),
                            'editor': row['editor'],
                            'image_id': row['image_id'],
                            'File_size': row['Filesize'],
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
@trashbin_data.route('/file/fetch_data/<image_id>', methods=['POST', 'GET'])
@login_required
@admin_required
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

@trashbin_data.route('/item-document/restore-file', methods=['POST', 'GET'])
@login_required
@admin_required
def restoreFile():
    if request.method == "POST":
        document_id = request.form.get('document_id')
        document_id = int(document_id)
        recover_query = restoreDocumentFile(document_id)

        if recover_query:
            return jsonify({'recover_query': recover_query})

@trashbin_data.route('/item-document/push-delete-permanent', methods=['POST', 'GET'])
@login_required
@admin_required
def permanent_deletion():

    if request.method == "POST":
        document_id = request.form.get('document_id')
        document_id = int(document_id)
        delete_query = deleteDocumentFile(document_id)

        if delete_query:
            return jsonify({'delete_query': delete_query})