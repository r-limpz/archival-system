from flask import Blueprint, request, jsonify, Response, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
import base64
from . import config

profile_data = Blueprint('account', __name__, url_prefix='/account/manage')

def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated and not current_user.is_active and current_user.role not in ['admin', 'staff']:
                return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

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

@profile_data.route('/user-profile/profile_details/account_status/list-progress/<username>', methods=['POST', 'GET'])
@login_required
@authenticate
def fetch_accountInfo(username):
    progress_report = getAccountData(username)
    data = {'account_id':username,'progress_report':progress_report}
    
    return jsonify(data)

