import pymysql

conn = pymysql.connect(host='localhost',
                       user='ards',
                       password='usep_20ards23//@-our',
                       database='rog',
                       cursorclass=pymysql.cursors.DictCursor)
