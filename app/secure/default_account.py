from app.database import config
from app.secure.randomizer import generate_key
from app import argon2 

def create_defaultAdmin(password):
    h_password = argon2.generate_password_hash(password)
    admin_account = {'username':'admin','fullname':'admin','password':h_password}

    try:
        with config.conn.cursor() as cursor:
            cursor.execute('INSERT INTO user (username, fullname, password, pass_key, role, status, online, last_online) VALUES (%s, %s, %s, %s, %s, %s, %s, NULL)', 
                        (admin_account['username'], admin_account['fullname'], admin_account['password'], generate_key() , 1, 1, 0) )
            config.conn.commit()

            new_id = cursor.lastrowid

            if new_id:
                return True
            
            return False

    except Exception as e:
        print(f"create Admin: {e}")

def generateAdmin():
    try:
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM user WHERE username = "admin"')
            admin_user = cursor.fetchone()

            default_admin_password = 'admin@1989'
            
            if admin_user:
                if argon2.check_password_hash(admin_user['password'], default_admin_password):
                    return True
                else:
                    return False
            return create_defaultAdmin(default_admin_password)
    except Exception as e:
        print(f"Search Admin: {e}")
