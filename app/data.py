from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from . import config

data_fetch = Blueprint('data', __name__)
from . import config


@data_fetch.route("/records_data",methods=["POST","GET"])
def records_data():
    try:
        with config.conn.cursor() as cursor:
            if request.method == 'POST':
                draw = request.form['draw'] 
                row = int(request.form['start'])
                rowperpage = int(request.form['length'])
                searchValue = request.form["search[value]"]
 
                ## Total number of records without filtering
                cursor.execute("select count(*) as allcount from srecordstbl")
                rsallcount = cursor.fetchone()
                totalRecords = rsallcount['allcount']
 
                ## Total number of records with filtering
                likeString = "%" + searchValue +"%"
                cursor.execute("SELECT count(*) as allcount from srecordstbl WHERE FullName LIKE %s OR College LIKE %s OR Course LIKE %s", (likeString, likeString, likeString))
                rsallcount = cursor.fetchone()
                totalRecordwithFilter = rsallcount['allcount']
 
                ## Fetch records
                if searchValue=='':
                    cursor.execute("SELECT * FROM srecordstbl ORDER BY FullName asc limit %s, %s;", (row, rowperpage))
                    recordlist = cursor.fetchall()
                else:        
                    cursor.execute("SELECT * FROM srecordstbl WHERE FullName LIKE %s OR College LIKE %s OR Course LIKE %s limit %s, %s;", (likeString, likeString, likeString, row, rowperpage))
                    recordlist = cursor.fetchall()
 
                data = []
                for row in recordlist:
                    data.append({
                        'id': row['id'],
                        'FullName': row['FullName'],
                        'College': row['College'],
                        'Course': row['Course'],
                        'Section': row['Section'],
                        'year_level': row['year_level'],
                        'Subject': row['Subject'],
                        'Unit': row['Unit'],
                        'Semester': row['Semester'],
                        'SchoolYear': row['SchoolYear'],
                    })
 
                response = {
                    'draw': draw,
                    'iTotalRecords': totalRecords,
                    'iTotalDisplayRecords': totalRecordwithFilter,
                    'aaData': data,
                }
                return jsonify(response)
    except Exception as e:
        print(e)
