from flask import Blueprint, request, jsonify, Response
from flask_login import login_required
import base64
from app.database import config
from app.tools.filesize_selector import filesize_format
from app.secure.authorization import admin_required

trashbin_data = Blueprint('trashbin', __name__, url_prefix='/admin/trash/manage/data')
    
def checkDuplicateFile(document_id):
    try:
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM documents WHERE filename = ( SELECT filename FROM documents WHERE docs_id = %s ) AND delete_status = 0', (document_id))
            result = cursor.fetchone()

            if result:
                return int(result['docs_id'])
        
            return None
    except Exception as e:
        print('Check Duplicate Filename Error:', e)

def fetchTags(document_id, status):
    try:
        with config.conn.cursor() as cursor:
            delete_status = {0: 'trash', 1: 'active', 99 : 'all'}.get(status, 1)

            if status == 'all':
                cursor.execute('SELECT student FROM tagging WHERE document = %s', (document_id))
                result = cursor.fetchall()
            else:
                cursor.execute('SELECT student FROM tagging WHERE document = %s AND delete_status = %s', (document_id, delete_status))
                result = cursor.fetchall()
                
            if result:
                return result
        
        return None
    except Exception as e:
        print('fetchTags Error:', e)

def restoreVersion(document_id, activeFile):
    try:
        with config.conn.cursor() as cursor:

            cursor.execute('DELETE FROM documents WHERE delete_status = 1 AND docs_id = %s', (activeFile,)) 
            config.conn.commit()

            if cursor.rowcount > 0:
                cursor.execute('UPDATE documents SET delete_status = 0 WHERE docs_id = %s', (document_id,)) 
                config.conn.commit()
                return 'success'

            return 'failed'
    except Exception as e:
            print('Recover data Error: ',e)

def restoreAsCopy(document_id, activeFile):
    try:
        with config.conn.cursor() as cursor:

            if cursor.rowcount > 0:
                cursor.execute("UPDATE documents SET filename = CONCAT(filename, '-copy'), delete_status = 0 WHERE docs_id = %s", (document_id,))
                config.conn.commit()
                return 'success'

            return 'failed'
    except Exception as e:
            print('Recover data Error: ',e)

def restoreMerge(document_id, activeFile, restoreType):
    try:
        with config.conn.cursor() as cursor:
            trashed_tags = fetchTags(document_id, restoreType)
            active_tags = fetchTags(activeFile, restoreType)

            trash_tagsList = []

            for trashed_item in trashed_tags:
                for active_item in active_tags:
                    if not trashed_item['student'] == active_item['student']:
                        trash_tagsList.append(trashed_item['student'])
                    else:
                        break

            success_counter = 0

            for item in trash_tagsList:
                try:
                    cursor.execute('INSERT INTO tagging (student, document) VALUES (%s, %s)', (item, activeFile))
                    config.conn.commit()
                    success_counter += 1

                except Exception as insert_error:
                    config.conn.rollback()  # Rollback on failure
                    print(f"Failed to insert {item} into tagging table: {insert_error}")

            if success_counter == len(trash_tagsList):
                return 'success'
            else:
                return 'failed'

    except Exception as e:
        print('Recover data Error: ', e)
        return 'failed'

# This will restore the record and update the existing record with the same details, including merging linked items.    
def restoreCustom(reference_document, customFile):
    try:
        activeFile = checkDuplicateFile(reference_document)

        if activeFile and restoreCustom:
            match customFile:
                case 'default': # Restore will delete new version to restore trashed version
                    return restoreVersion(reference_document, activeFile)
                case 'merge': # Restore will merge records tags
                    return restoreMerge(reference_document, activeFile)
                case 'copy': # Restore will merge records tags
                    return restoreAsCopy(reference_document, activeFile)

    except Exception as e:
            print('Recover default Error: ',e)

def restoreDocumentFile(document_id):
    try:
        with config.conn.cursor() as cursor:

            if not checkDuplicateFile(document_id):
                cursor.execute('UPDATE documents SET delete_status = 0 WHERE docs_id = %s', (document_id,)) 
                config.conn.commit()

                if cursor.rowcount > 0:
                    return 'success'
            else:
                return 'duplicate'
            
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

#fetch trash data for datatable
@trashbin_data.route("/fetch-data/deleted-files/trash-list",methods=["POST","GET"])
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
                            'Trash_date': row['Trash_date'].strftime('%B %d, %Y'),
                            'studentCount': row['studentCount'],
                            'editor': row['editor'],
                            'image_id': row['image_id'],
                            'File_size': filesize_format(row['Filesize']),
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

#restore file
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

#permanent delete one item
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

#clear all trashed data 
@trashbin_data.route('/all-document/clear-trashbin/push-delete-permanent', methods=['POST', 'GET'])
@login_required
@admin_required
def clear_trashbin():
    try:
        if request.method == "POST":
            randomString = request.form.get('value')

            if randomString:
                with config.conn.cursor() as cursor:
                    cursor.execute('''DELETE documents FROM documents INNER JOIN trashdocs ON documents.docs_id = trashdocs.document_id''')
                    rows_deleted = cursor.rowcount
                    config.conn.commit()

                    if rows_deleted > 0:
                        delete_query = 'success'
                    else:
                        delete_query = 'failed'

                    return jsonify({'delete_query': delete_query})
    except Exception as e:
            print('clear trashbin Error: ',e)