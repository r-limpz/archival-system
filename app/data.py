from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from flask import current_app as app
from . import config

data_fetch = Blueprint('data', __name__)

@data_fetch.route('/records_data', methods=['GET', 'POST'])
@login_required
def records_data():
    if current_user.is_authenticated:
        cursor = config.conn.cursor()
        
        if request.method =='POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            column_index = request.form['order[0][column]']
            sort_direction = request.form['order[0][dir]']
            searchValue = request.form['search[value]']
            likeString = "%" + searchValue + "%"
            
            # Total count data
            cursor.execute('SELECT COUNT(*) AS ALLCOUNT FROM srecordstbl' )
            rsallcounts = cursor.fetchone()
            totalRecords = rsallcounts['ALLCOUNT']
            
            # Total count with filter
            cursor.execute('SELECT COUNT(*) AS ALLCOUNT FROM srecordstbl WHERE FullName LIKE %s OR College LIKE %s OR Course LIKE %s OR year_level LIKE %s OR Subject LIKE %s OR Semester LIKE %s OR SchoolYear LIKE %s', (likeString, likeString, likeString, likeString, likeString, likeString, likeString))
            rsallcounts = cursor.fetchone()
            totalRecordswFilter = rsallcounts['ALLCOUNT']
            
            # feth all data records
            if searchValue == '':   
                cursor.execute(f'SELECT * FROM srecordstbl ORDER BY {column_index} {sort_direction} LIMIT %s, %s;', (row, rowperpage))
                student_records = cursor.fetchall()
            else:
                cursor.execute(f'SELECT * FROM srecordstbl WHERE FullName LIKE %s OR College LIKE %s OR Course LIKE %s OR year_level LIKE %s OR Subject LIKE %s OR Semester LIKE %s OR SchoolYear LIKE %s ORDER BY {column_index} {sort_direction} LIMIT %s, %s;', (likeString, likeString, likeString, likeString, likeString, likeString, likeString, row, rowperpage))
                student_records = cursor.fetchall()

            # Convert your data to a format that DataTables can read
            data = []
            for row in student_records:
                data.append({ 
                            'id' : row['id'],
                            'FullName' : row['FullName'],
                            'College' : row['College'],
                            'Course' : row['Course'],
                            'year_level' : row['year_level'],
                            'Subject' : row['Subject'],
                            'Semester' : row['Semester'],
                            'SchoolYear' : row['SchoolYear'] 
                            })

            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordswFilter,
                'aaData': data,
                }
            
            return jsonify(response)