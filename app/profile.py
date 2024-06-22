from flask import Blueprint, request, jsonify, Response, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
import calendar
from datetime import datetime, timedelta, date
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

# get the daily count of the month 
def get_countDaily(input_date, account):
    try:
        with config.conn.cursor() as cursor:
        
            # Extract the year and month from the input date
            input_year = input_date.year
            input_month = input_date.month

            days_in_month = calendar.monthrange(input_year, input_month)[1]
            daily_counts = {str(day): 0 for day in range(1, days_in_month + 1)}

            # Query to get counts per day within the input month
            cursor.execute('SELECT DAY(Upload_date) as day, COUNT(*) as count FROM documentstbl WHERE YEAR(Upload_date) = %s AND MONTH(Upload_date) = %s AND Uploader = %s GROUP BY day', (input_year, input_month, account))
            count_results = cursor.fetchall()

            # Update the dictionary with actual counts
            for row in count_results:
                daily_counts[str(row['day'])] = row['count']
            
            results = [{'label': str(day), 'count': count} for day, count in daily_counts.items()]

            return results
        
    except Exception as e:
        print(f"Error fetching daily data: {e}")

#get the total count per day within a week
def get_countWeekly(input_date, account):
    try:
        with config.conn.cursor() as cursor:
            days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            # Get the start and end dates of the week
            start_of_week = input_date - timedelta(input_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)

            # Query to count uploads for each day of the week
            cursor.execute(f"SELECT DAYNAME(Upload_date) as day, COUNT(*) as count FROM documentstbl WHERE Uploader = %s AND Upload_date BETWEEN '{start_of_week}' AND '{end_of_week}' GROUP BY day", (account))
            count_results = cursor.fetchall()

            # Initialize a dictionary to hold counts for each day
            day_counts = {day: 0 for day in days_of_week}

            # Update day_counts with actual counts from query results
            for row in count_results:
                if row['day'] in day_counts:
                    day_counts[row['day']] = row['count']

            # Append dictionaries with 'label' and 'count' to results list
            results = [{'label': day, 'count': day_counts[day]} for day in days_of_week]

            # Check if any day has a count of 0 and add it to results
            for day in days_of_week:
                if day not in day_counts:
                    results.append({'label': day, 'count': 0})
            
        return results
    except Exception as e:
        print('fetch data week: ', e)

# get monthly total counts within a year
def get_countMonthly(input_date, account):
    try:
        with config.conn.cursor() as cursor:
            # Parse the input date and extract the year
            input_year = input_date.year
            monthly_counts = {f"{calendar.month_abbr[i]}": 0 for i in range(1, 13)}

            cursor.execute('SELECT DATE_FORMAT(Upload_date, "%%Y-%%m") as month, COUNT(*) as count FROM documentstbl WHERE YEAR(Upload_date) = %s AND Uploader = %s GROUP BY month', (input_year, account))
            count_results = cursor.fetchall()

            for row in count_results:
                year, month = row['month'].split('-') 
                month_abbr = calendar.month_abbr[int(month)]
                monthly_counts[f"{month_abbr}"] = row['count']
                    
            results = [{'label': month, 'count': count} for month, count in monthly_counts.items()]

            return results

    except Exception as e:
        print(f"Error fetching monthly data: {e}")

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
    input_date = date.today()
    
    if progress_report:
        if len(progress_report)<=7:
            chartData = get_countWeekly(input_date, username)
        elif len(progress_report)>7 and len(progress_report)<=30:
            chartData = get_countDaily(input_date, username)
        elif len(progress_report)>30 and len(progress_report)<=12 :
            chartData = get_countMonthly(input_date, username)
    else:
        chartData = get_countWeekly(input_date, username)

    data = {'account_id':username,'progress_report':progress_report, 'chartData':chartData}
    
    if data:
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