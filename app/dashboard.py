from flask import Blueprint, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
import calendar
from datetime import datetime, timedelta
from . import config

dashboard_data = Blueprint('dashboard', __name__, url_prefix='/admin/dashboard/manage/data')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated and current_user.role != 'admin' or not current_user.is_active:
            return redirect(url_for('home'))
        elif current_user.is_authenticated and current_user.is_active and current_user.role == 'staff':
            return redirect(url_for('staff.records'))
        return f(*args, **kwargs)
    return decorated_function

# calculate the increased percentage per month
def calculate_percentage_increase(initial, new):
    increase = new - initial
    percentage_increase = (increase / initial) * 100
    return f"{percentage_increase:.2f}"

# format the count value
def format_count(count):
    if count >= 500000:
        return '{:.2f} M'.format(count / 1000000)
    else:
        return '{:,}'.format(count)
    
# convert the bytes value into a most efficient format KB/MB/GB
def filesize_format(filesize):
    if filesize >= 1024 * 1024 * 1024:  # Greater than or equal to 1 GB
        formatted_size = f"{filesize / (1024 * 1024 * 1024):.2f} GB"
    elif filesize >= 1024 * 1024:  # Greater than or equal to 1 MB
        formatted_size = f"{filesize / (1024 * 1024):.2f} MB"
    else:
        formatted_size = f"{filesize / 1024:.2f} KB"
    
    return formatted_size

# get the daily count of the month 
def get_countDaily(input_date):
    try:
        with config.conn.cursor() as cursor:
        
            # Extract the year and month from the input date
            input_year = input_date.year
            input_month = input_date.month

            days_in_month = calendar.monthrange(input_year, input_month)[1]
            daily_counts = {str(day): 0 for day in range(1, days_in_month + 1)}

            # Query to get counts per day within the input month
            cursor.execute('SELECT DAY(Upload_date) as day, COUNT(*) as count FROM documentstbl WHERE YEAR(Upload_date) = %s AND MONTH(Upload_date) = %s GROUP BY day', (input_year, input_month))
            count_results = cursor.fetchall()

            # Update the dictionary with actual counts
            for row in count_results:
                daily_counts[str(row['day'])] = row['count']
            
            results = [{'label': str(day), 'count': count} for day, count in daily_counts.items()]

            return results
        
    except Exception as e:
        print(f"Error fetching daily data: {e}")

#get the total count per day within a week
def get_countWeekly(input_date):
    try:
        with config.conn.cursor() as cursor:
            days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            # Get the start and end dates of the week
            start_of_week = input_date - timedelta(input_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)

            # Query to count uploads for each day of the week
            cursor.execute(f"SELECT DAYNAME(Upload_date) as day, COUNT(*) as count FROM documentstbl WHERE Upload_date BETWEEN '{start_of_week}' AND '{end_of_week}' GROUP BY day")
            count_results = cursor.fetchall()

            # Initialize a dictionary to hold counts for each day
            day_counts = {day: 0 for day in days_of_week}

            # Update day_counts with actual counts from query results
            for row in count_results:
                if row['day'] in day_counts:
                    day_counts[row['day']] = row['count']

            # Append dictionaries with 'label' and 'count' to results list
            results = [{'label': day, 'count': day_counts[day]} for day in days_of_week]
            
        return results
    except Exception as e:
        print('fetch data week: ', e)

# get monthly total counts within a year
def get_countMonthly(input_date):
    try:
        with config.conn.cursor() as cursor:
            # Parse the input date and extract the year
            input_year = input_date.year
            monthly_counts = {f"{calendar.month_abbr[i]}": 0 for i in range(1, 13)}

            cursor.execute('SELECT DATE_FORMAT(Upload_date, "%%Y-%%m") as month, COUNT(*) as count FROM documentstbl WHERE YEAR(Upload_date) = %s GROUP BY month', (input_year,))
            count_results = cursor.fetchall()

            for row in count_results:
                year, month = row['month'].split('-') 
                month_abbr = calendar.month_abbr[int(month)]
                monthly_counts[f"{month_abbr}"] = row['count']
                    
            results = [{'label': month, 'count': count} for month, count in monthly_counts.items()]

            return results

    except Exception as e:
        print(f"Error fetching monthly data: {e}")

# get the yearly count from initial up to 10 years
def get_countYearly():
    try:
        with config.conn.cursor() as cursor:
            # Get the earliest upload date
            cursor.execute('SELECT MIN(Upload_date) as min_date FROM documentstbl')
            min_date = cursor.fetchone()['min_date']
            start_year = min_date.year
            end_year = start_year + 9
            yearly_counts = {str(year): 0 for year in range(start_year, end_year + 1)}

            # Query to get counts per year within the 10-year range
            cursor.execute( 'SELECT YEAR(Upload_date) as year, COUNT(*) as count FROM documentstbl WHERE YEAR(Upload_date) BETWEEN %s AND %s GROUP BY year', (start_year, end_year) )
            count_results = cursor.fetchall()
            
            # Update the dictionary with actual counts
            for row in count_results:
                yearly_counts[str(row['year'])] = row['count']
            
            results = [{'label': year, 'count': count} for year, count in yearly_counts.items()]
            
            return results
        
    except Exception as e:
        print(f"Error fetching yearly data: {e}")

# determine the time format and range to populate on the dashboard chart
def fetchData(dataToFetch, start_date):
    with config.conn.cursor() as cursor:
        if dataToFetch:
            match dataToFetch:
                case 'daily':
                    data = get_countDaily(start_date)
                    return data

                case 'weekly':
                    data = get_countWeekly(start_date)
                    return data

                case 'monthly':
                    data = get_countMonthly(start_date)
                    return data

                case 'yearly':
                    data = get_countYearly()
                    return data

        return None

#determine the number of increased and decreased in percentage between current and last month
def getIncreaseData():
    with config.conn.cursor() as cursor:
        # Get the current year and month
        current_date = datetime.now().date()
        current_year = current_date.year
        current_month = current_date.month

        # Calculate last month's year and month
        last_month_date = current_date - timedelta(days=current_date.day)
        last_month_year = last_month_date.year
        last_month_month = last_month_date.month

        # Get this month's document count
        cursor.execute('SELECT COUNT(*) as count FROM documentstbl WHERE YEAR(Upload_date) = %s AND MONTH(Upload_date) = %s', (current_year, current_month))
        new_value = cursor.fetchone()['count']

        # Get last month's document count
        cursor.execute('SELECT COUNT(*) as count FROM documentstbl WHERE YEAR(Upload_date) = %s AND MONTH(Upload_date) = %s', (last_month_year, last_month_month))
        old_value = cursor.fetchone()['count']

        # Calculate the difference
        if old_value > 0:
            percentage_difference  = calculate_percentage_increase(old_value, new_value)
            return percentage_difference
        
        return None

# fetch data total count and storage size of the database
def getStatus_db():
    try:
        with config.conn.cursor() as cursor:

            result = {
            'documents_count': 0,
            'records_count': 0,
            'database_size': '',
            'trash_count': 0,
            'trash_size': '',
            'documents_status': 0,
            }

            result['documents_status'] = getIncreaseData() if getIncreaseData() is not None else 0
            # Get documents count
            cursor.execute('SELECT COUNT(*) AS doc_count FROM documentstbl')
            documents = cursor.fetchone()
            result['documents_count'] = format_count(documents['doc_count'] if documents['doc_count'] is not None else 0)

            # Get records count
            cursor.execute('SELECT COUNT(DISTINCT FullName) AS student_count FROM srecordstbl')
            records = cursor.fetchone()
            result['records_count'] = format_count(records['student_count'] if records['student_count'] is not None else 0)
            
            # Get trash count and size
            cursor.execute('SELECT COUNT(*) as trashCount, COALESCE(SUM(Filesize), 0) as sizes FROM trashtbl')
            trash_data = cursor.fetchone()
            result['trash_count'] = format_count(trash_data['trashCount'] if trash_data['trashCount'] is not None else 0)
            result['trash_size'] = filesize_format(trash_data['sizes'])

            # Get database size in MB
            cursor.execute("SELECT ROUND(SUM(data_length + index_length), 0) AS 'db_size' FROM information_schema.tables WHERE table_schema = 'ards_archives'")
            db = cursor.fetchone()
            result['database_size'] = filesize_format(db['db_size'])

            return result
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

#setup route to fetch data needed for the dashboard
@dashboard_data.route('/fetch/statistics-results/filtered', methods=['POST', 'GET'])
@login_required
@admin_required
def fetchdata():
    if request.method == 'POST':
        option = request.form.get('option')
        started_date_str = request.form.get('started_date')

        # Check if started_date_str is not empty and is a string
        if started_date_str:
            if isinstance(started_date_str, str):
                started_date = datetime.strptime(started_date_str, '%Y-%m-%d').date()
            else:
                started_date = started_date_str
        else:
            started_date = ''

        progress = fetchData(option, started_date)
        db_status = getStatus_db()

        data = {'progress':progress, 'db_status':db_status}

        if data:
            return jsonify(data)
        
        return None

