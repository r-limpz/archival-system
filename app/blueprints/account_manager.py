from flask import Blueprint, request, redirect, render_template, jsonify, url_for
from flask_login import login_required
from app.database import config
import argon2
from app.tools.date_formatter import onlineStatus, sched_accountDeletion
from app.secure.randomizer import generate_key
from app.secure.authorization import admin_required

account_manager = Blueprint('account_manager', __name__,url_prefix='/admin/user-manager/manage/data')

# role format function
def get_role(role):
    if not role:
        return 0
    else:
        #if the input type is string use dictionary fixed values
        if isinstance(role, str) and len(role) > 1: 
            return {'admin': 1, 'staff':2}.get(role, 2)
        # convert it to integer instead   
        elif role in [1, 2 ,'1', '2']: 
            return int(role)
    
#fetch all uer accounts
def fetchallAccount(displayController):
    if not displayController:
        return None
    else:
        # Split the displayController into status and role
        inputstate = displayController.split('-')
        def_status = inputstate[0]
        def_role = inputstate[1]

        # Map the status and role to their corresponding values
        status = {'active': 1, 'deactivated': 0, 'all': 99}.get(def_status)
        role = {'admin': 1, 'staff': 2, 'any': 99}.get(def_role)

        # Initialize the query and parameters
        query = 'SELECT user_id, fullname, username, online, last_online, status, role FROM user WHERE 1=1'
        params = []

        # Add the appropriate conditions to the query based on the status and role
        if status != 99:
            query += ' AND status = %s'
            params.append(status)
        if role != 99:
            query += ' AND role = %s'
            params.append(role)

        try:
            with config.conn.cursor() as cursor:
                # Execute the query
                cursor.execute(query, tuple(params))
                users = cursor.fetchall()

                cursor.execute('SELECT * FROM removed_sched_deact WHERE 1=1')
                deleted_accounts = cursor.fetchall()
                # If users are found, create a list of user dictionaries
                if users:
                    users_list = []

                    for user in users:
                        del_status = 'deleted' if any(deleted['user_id'] == user['user_id'] for deleted in deleted_accounts) else None
                        expected_removed = next((deleted['sched_removal'] for deleted in deleted_accounts if deleted['user_id'] == user['user_id']), None)

                        if user['last_online'] and not expected_removed:
                            last_online = onlineStatus(user['last_online'])
                        if expected_removed:
                            last_online = sched_accountDeletion(expected_removed) if expected_removed else None
                        else:
                            last_online = "Online Now" if user['online'] == 1 else "No activity yet"

                        users_list.append({
                            'user_id': user['user_id'],
                            'fullname': user['fullname'],
                            'username': user['username'],
                            'last_online': last_online,
                            'online': {1: 'online', 0: 'offline'}.get(user['online']),
                            'status': {0: 'deactivated', 1: 'active'}.get(user['status']),
                            'role': {1: 'admin', 2: 'staff'}.get(user['role']),
                            'deleteStatus': del_status,
                            'sched_deletion': expected_removed
                        })
                    return users_list
            return None

        except Exception as e:
            print(f"An error occurred while fetching all accounts: {e}")

#check duplicate entries
def checkDuplicateAccount(user_id, credential, dataSearch):
    if not user_id and not credential and not dataSearch:
        return False
    else:
        user_id = int(user_id)
        credential = {'username': 'username', 'fullname': 'fullname'}.get(credential, 'fullname')

        # Initialize the query and parameters
        query = 'SELECT user_id FROM user WHERE 1=1'
        params = []

        # Add the appropriate condition to the query based on the credential
        if credential == 'username':
            query += ' AND username = %s'
            params.append(dataSearch)
        elif credential == 'fullname':
            query += ' AND fullname = %s'
            params.append(dataSearch)
        
        # Exclude the current user_id from the search
        if not user_id == 0:
            query += ' AND NOT user_id = %s'
            params.append(user_id)

        try:
            with config.conn.cursor() as cursor:
                # Execute the query
                cursor.execute(query, tuple(params))
                search_result = cursor.fetchone()

                # Return True if a duplicate account is found, False otherwise
                if search_result:
                    return True
                else:
                    return False

        except Exception as e:
            print(f"An error occurred while checking for duplicate accounts: {e}")

# account creation function
def addNewUser( add_fullname, add_username, add_password):

    if not add_fullname and not add_username and not add_password:
        return 'failed'
    else:
        try:
            with config.conn.cursor() as cursor: 
                # Check if the username or fullname already exists
                usernameExists = checkDuplicateAccount(0, 'username', add_username)
                fullnameExists = checkDuplicateAccount(0, 'fullname', add_fullname)

                # If the username or fullname does not exist, proceed with adding the new user
                if not usernameExists and not fullnameExists:
                    h_password = argon2.generate_password_hash(add_password) # Generate a hashed password and a new pass_key
                    pass_key = generate_key()
                    role = 2 # Define the role and status for the new user

                    # Insert the new user data into the database
                    cursor.execute('INSERT INTO user (username, fullname, password, pass_key, role, status, online, last_online) VALUES (%s, %s, %s, %s, %s, %s, %s, NULL)',
                                (add_username, add_fullname, h_password, pass_key , role, 1, 0) )
                    config.conn.commit()
                    # Check if the user creation was successful
                    cursor.execute('SELECT user_id FROM user WHERE username = %s', (add_username))
                    insertSuccess = cursor.fetchone()

                    # Set the return value based on the success of the user creation
                    if insertSuccess:
                        data = 'success'
                    else:
                        data = 'failed'
                else:
                    data = 'duplicate user'
                return data
            
        except Exception as e:
                print(f"addNewUser() : {e}")
    
# dynamic update user data function
def updateAccount(user_id, fullname, username, role, password):
    # Initialize the query and parameters
    query = 'UPDATE user SET '
    params = []
    hasChanged = {}
    role = get_role(role) # Convert the role to its corresponding value

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

                    # If the password has changed, add it to the query and parameters
                if password and not argon2.check_password_hash(user['password'], password):
                    query += 'password = %s, '
                    hashed_password = argon2.generate_password_hash(password)
                    params.append(hashed_password)
                    hasChanged.update({"password": hashed_password})

                # Remove the trailing comma and space from the query
                query = query.rstrip(', ')
                query += ' WHERE user_id = %s'
                params.append(user_id)
                    
                # Execute the update query
                cursor.execute(query, tuple(params))
                config.conn.commit()

                # Verify if the update was successful
                keys_str = ', '.join(list(hasChanged.keys()))
                verifyQuery = 'SELECT '+ keys_str + ' FROM user WHERE user_id = %s'
                cursor.execute(verifyQuery, (user_id,))
                user_update = cursor.fetchone()

                if user_update == hasChanged:
                    return 'success'
                else:
                    return 'failed'
                
    except Exception as e:
        print(f"updateAccount() : {e}")

#temporary disbale and delete account schedule
def removeAccount(profile_id):
    try:
        with config.conn.cursor() as cursor:
            profile_id = int(profile_id)

            cursor.execute('SELECT * FROM user WHERE user_id =%s', (profile_id))
            userExist = cursor.fetchone()

            if userExist:
                cursor.execute('INSERT IGNORE INTO removed_sched_deact (user_id, removed_date, sched_removal) VALUES (%s, NOW(), DATE_ADD(NOW(), INTERVAL 30 DAY))', (profile_id))
                config.conn.commit()

                cursor.execute('SELECT * FROM removed_sched_deact WHERE user_id =%s', (profile_id))
                schedExist = cursor.fetchone()

                if schedExist:
                    query = 'success'
                else:
                    query = 'failed'

                return query
            
            else:
                return 'failed'
    except Exception as e:
        print(f"removeAccount() : {e}")

#setup route to fetch account list 
@account_manager.route('/fetch/users-list/filter-status/<active_status>')
@login_required
@admin_required
def users_list(active_status):
    if not active_status:
        return jsonify(None)
    else:
        try:
            users_list = fetchallAccount(active_status)
            if users_list:
                return jsonify(users_list)
            else:
                return jsonify(None)
        except Exception as e:
            print(f"display user error occurred: {e}")

#setup route to preview an account data 
@account_manager.route('/user/preview-profile/account-id/<profile_id>')
@login_required
@admin_required
def preview_account(profile_id):
    if not profile_id:
        return redirect(url_for('account_manager'))
    else:
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

#setup route to create an user account
@account_manager.route('/new-user/data-credentials/register-account' , methods=['POST', 'GET'])
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

#setup route to update account status activate/deactivated
@account_manager.route('/user/account-status/update', methods=['POST', 'GET'])
@login_required
@admin_required
def change_status():
    if request.method == "POST":
        user_id = request.form.get('user_id')
        status = request.form.get('user_state')

        user_id = int(user_id)
        status = int({'active': 1, 'deactivated': 0}.get(status))

    try:
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT status FROM user WHERE user_id = %s', (user_id,))
            current_status = cursor.fetchone()

            if not current_status or current_status['status'] != status:
                cursor.execute('UPDATE user SET status = %s WHERE user_id = %s', (status, user_id))
                config.conn.commit()

                if status == 0:
                    cursor.execute('DELETE FROM session WHERE user_id = %s', (user_id,))
                    config.conn.commit()

                cursor.execute('SELECT * FROM user WHERE status = %s AND user_id = %s', (status, user_id))
                status_changed = cursor.fetchone()

                if status_changed:
                    return jsonify({'change_state': 'success'})
                else:
                    return jsonify({'change_state': 'failed'})
            else:
                return jsonify({'change_state': 'no changes applied'})

    except Exception as e:
        print(f"change status error occurred: {e}")

#setup route to fetch account credentials for editing 
@account_manager.route('/user/fetch/account-credentials/account-id/<profile_id>')
@login_required
@admin_required
def manage_user(profile_id):
    if profile_id:
        try:
            with config.conn.cursor() as cursor:
                cursor.execute('SELECT * FROM user WHERE user_id = %s', (profile_id))
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
    else:
        return jsonify('error, user not found')

#setup route to update account credentials
@account_manager.route('/user/update/account-credentials/new-data', methods=['POST', 'GET'])
@login_required
@admin_required
def edit_user():
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

                if update_status:
                    return jsonify({'update_query': update_status})
                else:
                    return jsonify({'update_query': 'error occured'})
            else:
                return jsonify({'update_query': 'incorrect password'})
                
    except Exception as e:
            print(f"update user credentials  error occurred: {e}")

#setup route to deactivate and account for deletion 30 days permanent deletion
@account_manager.route('/user/update/account-status/deactivate/delete', methods=['POST', 'GET'])
@login_required
@admin_required
def account_delete():
    try:
        if request.method == "POST":
            data = request.get_json()
            profile_id = data.get('user_data')

            query = removeAccount(profile_id)

            if query:
                return jsonify({'delete_query': query})
            else:
                return jsonify({'delete_query': 'failed'})
        
    except Exception as e:
            print(f"delete user error occurred: {e}")

#setup route to veirfy credenials unique or duplicate
@account_manager.route('/fetch/users-list/find-duplicates/verify-status/', methods=['POST', 'GET'])
@login_required
@admin_required
def check_inputVerify():
    if request.method == "POST":
        user_id = request.form.get('profile_id')
        credential = request.form.get('credential')
        dataSearch = request.form.get('dataSearch')
    try:
        verifyResult = checkDuplicateAccount(user_id, credential, dataSearch)
        verifyResult = {True: 'true', False:'false' }.get(verifyResult)
        
        if verifyResult:
            return jsonify({'is_nameExist': verifyResult})
        else:
            return jsonify({'is_nameExist': 'false'})
        
    except Exception as e:
        print(f"An error occurred while verifying the uniqueness of the user input: {e}")

            
       