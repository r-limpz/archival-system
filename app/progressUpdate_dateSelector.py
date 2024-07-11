from . import config
import calendar
from datetime import timedelta

def get_countAll(account):
    try:
        with config.conn.cursor() as cursor:
            cursor.execute("SELECT MIN(Upload_date) as min_date, MAX(Upload_date) as max_date FROM documentstbl")
            min_max_dates = cursor.fetchone()

            start_date_obj = min_max_dates['min_date'].date()
            end_date_obj = min_max_dates['max_date'].date()

            if start_date_obj and end_date_obj:
                date_diff = (end_date_obj - start_date_obj).days
            else:
                date_diff = 0

            if date_diff <= 7:
                return get_countWeekly(start_date_obj, account)
            elif date_diff >7 and date_diff <= 31:
                return get_countDaily(start_date_obj, account)
            elif date_diff >31 and date_diff <= 365:
                return get_countMonthly(start_date_obj, account)
            
    except Exception as e:
        print('fetch data all: ', e)

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