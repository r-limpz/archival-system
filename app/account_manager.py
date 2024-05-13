from flask import Blueprint, request, redirect, render_template, jsonify, url_for, abort
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
import secrets
import string
from flask import current_app as app
from . import config, login_manager, argon2

account_manager = Blueprint('user_controller', __name__,url_prefix='/ards/admin/account_manager')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated() and current_user.role != 'admin' or not current_user.is_active():
            return redirect(url_for('home'))
        elif current_user.is_authenticated() and current_user.is_active() and current_user.role == 'staff':
            return redirect(url_for('records'))
        return f(*args, **kwargs)
    return decorated_function

def get_currentTime(last_online):
    now = datetime.now()
    diff = now - last_online

    weeks, days = divmod(diff.days, 7)
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if weeks > 0:
        if days > 0:
            last_online_str = f"{weeks} weeks and {days} days ago"
        else:
            last_online_str = f"{weeks} weeks ago"
    elif days > 0:
        last_online_str = f"{days} days ago"
    elif hours > 0:
        last_online_str = f"{hours} hours and {minutes} minutes ago"
    elif minutes > 0:
        last_online_str = f"{minutes} minutes ago"
    else:
        last_online_str = f"{seconds} seconds ago"

    return last_online_str

def generate_key(length=256):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for i in range(length))

def createAccount(username, fullname, role, password):
    try:
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT user_id FROM user WHERE username = %s, fullname = %s role = %s', (username, fullname, role))
            userExist = cursor.fetchone()

            if not userExist:
                cursor.execute('INSERT INTO user(username, role, password, key, status, online) ', (username, role, argon2.generate_password_hash(password), generate_key(), 1, 0))
                config.conn.commit()

                cursor.execute('SELECT user_id FROM user WHERE username = %s', (username))
                insertSuccess = cursor.fetchone()

                if insertSuccess:
                    return 'success'
                else:
                    return 'failed'
            else:
                return 'duplicate'

    except Exception as e:
            print(f"create user error occurred: {e}")

def updateAccount(user_id, fullname, role, status, password):
    try:
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM user WHERE user_id = %s', (user_id,))
            user = cursor.fetchone()
            hashed_password = argon2.generate_password_hash(password)

            if isinstance(role, str) and len(role) > 1:
                role = {'admin': 1, 'staff':2}.get(role, 2)
            elif role in [1, 2 ,'1', '2']:    
                role = int(role)
            else:
                role = 2
                
            if user:
                cursor.execute('UPDATE user SET fullname = %s, role = %s, password = %s, key = %s, status = %s WHERE user_id = %s', (fullname, role, hashed_password, generate_key(), status, user_id))
                config.conn.commit()

                cursor.execute('SELECT * FROM user WHERE user_id = %s', (user_id))
                user_update = cursor.fetchone()

                if user_update['fullname'] == fullname and user_update['role'] == role and argon2.check_password_hash(user_update['password'], password):
                    return 'success'
                else:
                    return 'failed'
            else:
                return 'user not found'

    except Exception as e:
            print(f"create user error occurred: {e}")

@account_manager.route('/display_staff_users')
@login_required
@admin_required
def users_list():
    try:
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT user_id, fullname, username,  online, last_online, status, role FROM user WHERE role = %s', (2))
            users = cursor.fetchall()
            users_list = []
            for user in users:
                user_dict = {
                    'user_id': user['user_id'],
                    'fullname': user['fullname'],
                    'username': user['username'],
                    'last_online': get_currentTime(user['last_online']) if user['last_online'] else 'Now',
                    'online': {1: 'online', 0: 'offline'}.get(user['online']),
                    'status': {0: 'deactivated', 1: 'active'}.get(user['status']),
                    'role': {1: 'admin', 2: 'staff'}.get(user['role'])
                }
                users_list.append(user_dict)
        return jsonify(users_list)
    
    except Exception as e:
         print(f"display user error occurred: {e}")

@account_manager.route('/preview/<user_id>')
@login_required
@admin_required
def preview(user_id):
     pass

@account_manager.route('/remove/<user_id>', methods=['POST'])
@login_required
@admin_required
def remove_user(user_id):
    try:
        with config.conn.cursor() as cursor:
            cursor.execute('UPDATE user SET status = 0 WHERE user_id = %s', (user_id))
            config.conn.commit

            cursor.execute('SELECT * FROM user WHERE user_id = %s AND status = 0', (user_id))
            user_deactivate = cursor.fetchone

            if not user_deactivate:
                return jsonify({'success': True})
            else:
                return jsonify({'success': False})
            
    except Exception as e:
         print(f"remove user error occurred: {e}")

@account_manager.route('/edit/<user_id>')
@login_required
@admin_required
def edit_user(user_id):
    # Render edit user page
    pass