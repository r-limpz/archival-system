from flask import Blueprint, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
import calendar
from datetime import datetime, timedelta
from . import config

dashboard_data = Blueprint('dashboard', __name__, url_prefix='/dashboard/manage/data')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated and current_user.role != 'admin' or not current_user.is_active:
            return redirect(url_for('home'))
        elif current_user.is_authenticated and current_user.is_active and current_user.role == 'staff':
            return redirect(url_for('staff.records'))
        return f(*args, **kwargs)
    return decorated_function

def get_countAll():
    try:
        with config.conn.cursor() as cursor:
            cursor.execute("SELECT MIN(Upload_date) as min_date, MAX(Upload_date) as max_date FROM documentstbl")
            min_max_dates = cursor.fetchone()

            start_date_obj = min_max_dates['min_date'].date()
            end_date_obj = min_max_dates['max_date'].date()
            date_diff = (end_date_obj - start_date_obj).days

            # Group by month if date difference is <= 1 year
            if date_diff <= 365:
                try:
                    monthly_counts = {f"{calendar.month_abbr[i]}": 0 for i in range(1, 13)}

                    cursor.execute("SELECT DATE_FORMAT(Upload_date, '%Y-%m') as month, COUNT(*) as count FROM documentstbl GROUP BY month")
                    count_results = cursor.fetchall()

                    for row in count_results:
                        year, month = row['month'].split('-')  # Split the 'YYYY-MM' format
                        month_abbr = calendar.month_abbr[int(month)]  # Get the full month name
                        monthly_counts[f"{month_abbr}"] = row['count']
                    
                    results = [{'label': month, 'count': count} for month, count in monthly_counts.items()]

                    return results
                
                except Exception as e:
                    print(f"Error fetching monthly data: {e}")

    except Exception as e:
        print('fetch data all: ', e)

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

def get_countWeekly(input_date):
    try:
        with config.conn.cursor() as cursor:
            days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            # Get the start and end dates of the week
            start_of_week = input_date - timedelta(input_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)

            print(start_of_week, end_of_week)

            # Query to count uploads for each day of the week
            cursor.execute(f"SELECT DAYNAME(Upload_date) as day, COUNT(*) as count FROM documentstbl WHERE Upload_date BETWEEN '{start_of_week}' AND '{end_of_week}' GROUP BY day")
            count_results = cursor.fetchall()

            print('query :',count_results)
            # Initialize a dictionary to hold counts for each day
            day_counts = {day: 0 for day in days_of_week}

            # Update day_counts with actual counts from query results
            for row in count_results:
                if row['day'] in day_counts:
                    day_counts[row['day']] = row['count']

            # Append dictionaries with 'label' and 'count' to results list
            results = [{'label': day, 'count': day_counts[day]} for day in days_of_week]
            print(results)
        return results
    except Exception as e:
        print('fetch data week: ', e)

import calendar
from datetime import datetime

def get_countMonthly(input_date):
    try:
        with config.conn.cursor() as cursor:
            # Parse the input date and extract the year
            input_year = input_date.year
            monthly_counts = {f"{calendar.month_abbr[i]}": 0 for i in range(1, 13)}

            cursor.execute('SELECT DATE_FORMAT(Upload_date, "%%Y-%%m") as month, COUNT(*) as count FROM documentstbl WHERE YEAR(Upload_date) = %s GROUP BY month', (input_year,))
            count_results = cursor.fetchall()

            for row in count_results:
                year, month = row['month'].split('-')  # Split the 'YYYY-MM' format
                month_abbr = calendar.month_abbr[int(month)]  # Get the full month name
                monthly_counts[f"{month_abbr}"] = row['count']
                    
            results = [{'label': month, 'count': count} for month, count in monthly_counts.items()]

            return results

    except Exception as e:
        print(f"Error fetching monthly data: {e}")

def get_countYearly():
    try:
        with config.conn.cursor() as cursor:
            # Get the earliest upload date
            cursor.execute('SELECT MIN(Upload_date) as min_date FROM documentstbl')
            min_date = cursor.fetchone()['min_date']
            start_year = min_date.year
            end_year = start_year + 9

            # Initialize a dictionary to hold yearly counts for the 10-year range
            yearly_counts = {str(year): 0 for year in range(start_year, end_year + 1)}

            # Query to get counts per year within the 10-year range
            cursor.execute( 'SELECT YEAR(Upload_date) as year, COUNT(*) as count FROM documentstbl WHERE YEAR(Upload_date) BETWEEN %s AND %s GROUP BY year', (start_year, end_year)
            )
            count_results = cursor.fetchall()
            
            # Update the dictionary with actual counts
            for row in count_results:
                yearly_counts[str(row['year'])] = row['count']
            
            results = [{'label': year, 'count': count} for year, count in yearly_counts.items()]
            
            return results
        
    except Exception as e:
        print(f"Error fetching yearly data: {e}")

def fetchData(dataToFetch, start_date, end_date):
    with config.conn.cursor() as cursor:
        if dataToFetch:
            print(dataToFetch)
            match dataToFetch:
                case 'all':
                    data = get_countAll()
                    return data
                
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
    
from datetime import datetime

@dashboard_data.route('/fetch/statistics-results/filtered', methods=['POST', 'GET'])
@login_required
@admin_required
def fetchdata():
    if request.method == 'POST':
        option = request.form.get('option')
        started_date_str = request.form.get('started_date')
        end_date_str = request.form.get('end_date')

        # Check if started_date_str is not empty and is a string
        if started_date_str:
            if isinstance(started_date_str, str):
                started_date = datetime.strptime(started_date_str, '%Y-%m-%d').date()
            else:
                started_date = started_date_str
        else:
            started_date = ''

        # Check if end_date_str is not empty and is a string
        if end_date_str:
            if isinstance(end_date_str, str):
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            else:
                end_date = end_date_str  
        else:
            end_date = ''

        results = fetchData(option, started_date, end_date)

        if results:
            return jsonify(results)
        
        return None
