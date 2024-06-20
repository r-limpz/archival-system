from flask import Blueprint, request, jsonify, Response, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
import base64
from . import config

profile_data = Blueprint('account', __name__, url_prefix='/account/manage/user-profile')

def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated and not current_user.is_active and current_user.role not in ['admin', 'staff']:
                return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def filesize_format(filesize):
    if filesize >= 1024 * 1024 * 1024:  # Greater than or equal to 1 GB
        formatted_size = f"{filesize / (1024 * 1024 * 1024):.2f} GB"
    elif filesize >= 1024 * 1024:  # Greater than or equal to 1 MB
        formatted_size = f"{filesize / (1024 * 1024):.2f} MB"
    else:
        formatted_size = f"{filesize / 1024:.2f} KB"
    
    return formatted_size

def getAccountData(user_username):
    try:
        with config.conn.cursor() as cursor:
              
            progress_report =[]

            cursor.execute('SELECT YEAR(Upload_date) as year, MONTH(Upload_date) as month, DAY(Upload_date) as day, COUNT(*) as count FROM documentstbl WHERE Uploader = %s GROUP BY YEAR(Upload_date), MONTH(Upload_date), DAY(Upload_date) ORDER BY YEAR(Upload_date), MONTH(Upload_date), DAY(Upload_date)', (user_username))
            count_results = cursor.fetchall()
                    
            for row in count_results:
                progress_report.append({
                    'date': datetime(row['year'], row['month'], row['day']).strftime('%Y-%m-%d'),
                    'value': row['count']
                })
                    
            if progress_report:
                return progress_report
      
    except Exception as e:
        print(f"preview user route error occurred: {e}")

@profile_data.route('/profile_details/account_status/list-progress/<username>', methods=['POST', 'GET'])
@login_required
@authenticate
def fetch_accountInfo(username):
    progress_report = getAccountData(username)
    data = {'account_id':username,'progress_report':progress_report}
    
    return jsonify(data)

#fetch data for datatable
@profile_data.route("/account-logs/uploads",methods=["POST","GET"])
@login_required
@authenticate
def account_logs():
    try:
        if request.method == 'POST':
            draw = request.form.get('draw') 
            row = int(request.form.get('start'))
            rowperpage = int(request.form.get('length'))
            column_index = request.form.get('order[0][column]') # Column index
            column_name = request.form.get('columns['+column_index+'][data]') # Column name
            column_sort_order = request.form.get('order[0][dir]') # asc or desc

            account_username = request.form.get('account_username')
            search_query = ""

            if account_username:
                search_query += f" and (Uploader = '{account_username}')"

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
                    for row in recordlist:
                        data.append({
                            'id': row['id'],
                            'Filename': row['Filename'],
                            'File_size': filesize_format(row['Filesize']),
                            'Upload_date': row['Upload_date'].strftime('%B %d, %Y'),
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
        print('Fetch documents Error: ',e)

#preview document image
@profile_data.route('/account-logs/uploads/select-file/fetch_data/<image_id>', methods=['POST', 'GET'])
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