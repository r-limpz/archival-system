import pymysql

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       database='rog',
                       cursorclass=pymysql.cursors.DictCursor)
