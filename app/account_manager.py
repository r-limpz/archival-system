from flask import Blueprint, request, redirect, render_template, jsonify, url_for, abort
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
import secrets
import string
from flask import current_app as app
from . import config, argon2

account_manager = Blueprint('account_manager', __name__,url_prefix='/admin/account_manager')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated and current_user.role != 'admin' and not current_user.is_active:
            return redirect(url_for('home'))
        elif current_user.is_authenticated and current_user.is_active and current_user.role == 'staff':
            return redirect(url_for('staff.records'))
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
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for i in range(length))

def addNewUser( add_fullname, add_username, add_password):
    try:
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM user WHERE username = %s AND fullname = %s', (add_username, add_fullname))
            userExist = cursor.fetchone()

            if not userExist:
                h_password = argon2.generate_password_hash(add_password)
                pass_key = generate_key()
                role = 2

                cursor.execute('INSERT INTO user (username, fullname, password, pass_key, role, status, online, last_online) VALUES (%s, %s, %s, %s, %s, %s, %s, NULL)',
                               (add_username, add_fullname, h_password, pass_key , role, 1, 0) )
                config.conn.commit()

                cursor.execute('SELECT user_id FROM user WHERE username = %s', (add_username))
                insertSuccess = cursor.fetchone()

                if insertSuccess:
                    data = 'success'
                else:
                    data = 'failed'
            else:
                data = 'duplicate user'
            
            return data

    except Exception as e:
            print(f"create user error occurred: {e}")

def updateAccount(user_id, fullname, username, role, password):
    query = 'UPDATE user SET '
    params = []
    hasChanged = {}
    role = get_role(role)

    try:
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM user WHERE user_id = %s', (user_id,))
            user = cursor.fetchone()

            if not user:
                return 'user not found'
            else:
                if user['fullname'] != fullname:
                    query += 'fullname = %s, '
                    params.append(fullname)
                    hasChanged.update({"fullname": fullname})

                if user['username'] != username:
                    query += 'username = %s, '
                    params.append(username)
                    hasChanged.update({"username": username})

                if user['role'] != role:
                    query += 'role = %s, '
                    params.append(role)
                    hasChanged.update({"role": role})

                if password and not argon2.check_password_hash(user['password'], password):
                    query += 'password = %s, '
                    hashed_password = argon2.generate_password_hash(password)
                    params.append(hashed_password)
                    hasChanged.update({"password": hashed_password})

                query = query.rstrip(', ')  # remove trailing comma and space
                query += ' WHERE user_id = %s'
                params.append(user_id)
                cursor.execute(query, tuple(params))
                config.conn.commit()

                keys_str = ', '.join(list(hasChanged.keys()))
                
                verifyQuery = 'SELECT '+ keys_str + ' FROM user WHERE user_id = %s'
                cursor.execute(verifyQuery, (user_id,))
                user_update = cursor.fetchone()

                if user_update == hasChanged:
                    return 'success'
                else:
                    return 'failed'
                    
    except Exception as e:
        print(f"changeCredentials function error occurred: {e}")

def get_role(role):
    if isinstance(role, str) and len(role) > 1:
        return {'admin': 1, 'staff':2}.get(role, 2)
    elif role in [1, 2 ,'1', '2']:    
        return int(role)
    else:
        return 2

@account_manager.route('/display_staff_users/<active_status>')
@login_required
@admin_required
def users_list(active_status):
    if active_status:
        inputstate = active_status
        inputstate = inputstate.split('-')

        def_status = inputstate[0]
        def_role = inputstate[1]

        status = {'active': 1, 'deactivated': 0, 'all': 99}.get(def_status)
        role = {'admin': 1, 'staff': 2, 'any': 99}.get(def_role)

        query = 'SELECT user_id, fullname, username, online, last_online, status, role FROM user WHERE 1=1'
        params = []

        if status != 99:
            query += ' AND status = %s'
            params.append(status)

        if role != 99:
            query += ' AND role = %s'
            params.append(role)

        try:
            with config.conn.cursor() as cursor:
                cursor.execute(query, tuple(params))
                users = cursor.fetchall()

                if users:
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
                else:
                    return jsonify(None)
        
        except Exception as e:
            print(f"display user error occurred: {e}")

@account_manager.route('/preview/<profile_id>')
@login_required
@admin_required
def preview_account(profile_id):
    try:
        profile_id = int(profile_id)
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT fullname, username, role FROM user WHERE user_id = %s', (profile_id))
            profile = cursor.fetchone()

            if profile:
                return render_template ('users/preview-user.html', preview_fullname = profile['fullname'], preview_username = profile['username'], preview_role = {1: 'admin', 2: 'staff'}.get(profile['role']))
            else:
                return redirect(url_for('account_manager'))
            
    except Exception as e:
         print(f"preview user route error occurred: {e}")
    
@account_manager.route('/manage/new_user' , methods=['POST', 'GET'])
@login_required
@admin_required
def create_account():
    try:
        if request.method == "POST":
            fullname = request.form.get('newuser_fullname')
            username = request.form.get('newuser_username')
            password = request.form.get('newuser_password')
            re_password = request.form.get('newuser_repassword')
            
            if password == re_password:
                account_added = addNewUser(fullname, username, password)
                
                if account_added:
                    update_query = account_added
                else:
                    update_query = 'error occured'
            else:
                update_query = 'Password not the same'
                
            return jsonify({'update_query': update_query})
            
    except Exception as e:
         print(f"create user route error occurred: {e}")

@account_manager.route('/user_state/', methods=['POST'])
@login_required
@admin_required
def change_status():
    if request.method == "POST":
        user_id = request.form.get('user_id')
        status = request.form.get('user_state')
        user_id = int(user_id)
        status = {'active':1, 'deactivated':0 }.get(status)

    try:
        with config.conn.cursor() as cursor:
            cursor.execute('UPDATE user SET status = %s WHERE user_id = %s', (status, user_id))
            config.conn.commit()

            if status == 0:
                cursor.execute('DELETE FROM session WHERE user_id = %s', (user_id,))
                config.conn.commit()

            cursor.execute('SELECT * FROM user WHERE status = %s AND user_id = %s', ( status, user_id))
            status_changed = cursor.fetchone()

            if status_changed:
                update_query = 'success'
            else:
                update_query = 'failed'
            
            return jsonify({'change_state': update_query})
            
    except Exception as e:
         print(f"remove user error occurred: {e}")

@account_manager.route('/manage/<user_id>' , methods=['POST', 'GET'])
@login_required
@admin_required
def manage_user(user_id):
    try:
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT fullname, username, status, role FROM user WHERE user_id = %s', (user_id))
            user_info = cursor.fetchone()

            if user_info:
                user_credentials = {
                    'update_fullname': user_info['fullname'],
                    'update_username': user_info['username'],
                    'update_role' : user_info['role'],
                }
                return jsonify(user_credentials)
            else:
                return jsonify('error, user not found')
            
    except Exception as e:
         print(f"manage user error occurred: {e}")

@account_manager.route('/account/update', methods=['POST'])
@login_required
@admin_required
def edit_user():
    # Render edit user page
    try:
        if request.method == "POST":
            user_id = request.form.get('update_user_id')
            fullname = request.form.get('update_fullname')
            username = request.form.get('update_username')
            role = request.form.get('update_role')
            password = request.form.get('update_password')
            re_password = request.form.get('update_repassword')

            if password == re_password:
                update_status = updateAccount(user_id, fullname, username, role, password)
                print(update_status)

                if update_status:
                    return jsonify({'update_query': update_status})
                else:
                    return jsonify({'update_query': 'error occured'})
            else:
                return jsonify({'update_query': 'incorrect password'})
                
    except Exception as e:
            print(f"update user credentials  error occurred: {e}")

@account_manager.route('/verify-unique/textdata', methods=['POST'])
@login_required
@admin_required
def check_inputVerify():
    # Render edit user page
    if request.method == "POST":
        user_id = request.form.get('profile_id')
        credential = request.form.get('credential')
        dataSearch = request.form.get('dataSearch')

        user_id = int(user_id)
        credential = {'username': 'username', 'fullname': 'fullname'}.get(credential, 'fullname')

        query = 'SELECT user_id FROM user WHERE 1=1'
        params = []

        if credential == 'username':
            query += ' AND username = %s'
            params.append(dataSearch)
        
        elif credential == 'fullname':
            query += ' AND fullname = %s'
            params.append(dataSearch)
        
        if not user_id == 0:
            query += ' AND NOT user_id = %s'
            params.append(user_id)

        try:
            with config.conn.cursor() as cursor:
                cursor.execute(query, tuple(params))
                search_result = cursor.fetchone()

                if search_result:
                    verifyResult = 'true'
                else:
                    verifyResult = 'false'

            return jsonify({'is_nameExist': verifyResult})
        
        except Exception as e:
            print(f"verify unique user error occurred: {e}")
            
       