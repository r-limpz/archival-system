from . import config

#account history login
def loginHistory(user_id, session_data, user_info):
    with config.conn.cursor() as cursor:
        user_deviceInfo = user_info
        device = user_deviceInfo['device']
        browser = user_deviceInfo['browser']
        os = user_deviceInfo['os']
        ip_address = user_deviceInfo['ip_address']

        cursor.execute('SELECT * FROM login_history WHERE session_data = %s', (session_data,))
        current_history = cursor.fetchone()
     
        if not current_history:
            cursor.execute('INSERT INTO login_history(user_id, ip_address, session_data) VALUES (%s, %s, %s, %s)',
                           (str(user_id), ip_address, session_data))
            config.conn.commit()

