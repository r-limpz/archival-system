import pymysql

try:
    with pymysql.connect(host='localhost', user='ards', password='usep_20ards23//@-our', database='rog', cursorclass=pymysql.cursors.DictCursor):

        conn = pymysql.connect(host='localhost',
                            user='ards',
                            password='usep_20ards23//@-our',
                            database='rog',
                            cursorclass=pymysql.cursors.DictCursor)
        
except pymysql.Error as e:
    print(f"Database Connection Error: {e}")


