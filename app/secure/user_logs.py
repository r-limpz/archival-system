from app.database import config
import hashlib

#account history login
def loginHistory(user_id, session_data, user_info):
    with config.conn.cursor() as cursor:
        cursor.execute('SELECT * FROM login_history WHERE session_data = %s AND user_id = %s', (session_data, user_id))
        current_history = cursor.fetchone()

        if not current_history:
            cursor.execute('INSERT INTO login_history (user_id, ip_address, session_data) VALUES (%s, %s, %s)',
                           (user_id, user_info['ip_address'], session_data))
            config.conn.commit()


