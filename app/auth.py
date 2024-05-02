from flask import session, render_template, redirect, url_for, request, Blueprint
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
import bcrypt
import hmac
from datetime import datetime, timedelta
import secrets
import string
from . import config, login_manager, argon2, captcha
from flask import current_app as app
from .forms import LoginForm

auth = Blueprint('auth', __name__)

def generate_id(length=256):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for i in range(length))

def generate_token(data, key, key2):
    combined_data = str(data) + app.config['SECRET_KEY'] + key + key2
    salt = bcrypt.gensalt()
    hashcode = bcrypt.hashpw(combined_data.encode(), salt)
    return hashcode.decode()

def check_token(token, data, key , key2):
    hashed = generate_token(data, key , key2)
    return hmac.compare_digest(hashed, token)

class User(UserMixin):
    def __init__(self, id, username, role, token):
        self.id = id
        self.username  = username
        self.role = role
        self.token = token

    def get_User(self):
        try:
            with config.conn.cursor() as cursor:
                cursor.execute('SELECT * FROM session WHERE session_id = %s', (self.id,))
                user_session = cursor.fetchone()

                if user_session:
                    cursor.execute('SELECT status FROM user WHERE user_id = %s', (user_session['user_id'],))
                    return cursor.fetchone()
                else:
                    return None
        except Exception as e:
            print(f"search user error occurred: {e}")

    def is_authenticated(self):
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM session WHERE session_id = %s', (self.id,))
            user_session = cursor.fetchone()

            user = self.get_User()
            if user_session and user:
                if user_session['status'] == 1 and check_token(self.token, user['password'], user['key'],self.id):
                    isvalid = True
                else:
                    isvalid = False
            else:
                isvalid = False
        return isvalid

    def is_active(self):
        user = self.get_User()
        if user and user['status'] == 1 and user['online'] == 1:
            return True
        else:
            return False

@login_manager.user_loader
def load_user(session_id):
    try:
        with config.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM session WHERE session_id = %s', (session_id,))
            user_session = cursor.fetchone()

            if user_session:
                cursor.execute('SELECT * FROM user WHERE user_id = %s', (user_session['user_id'],))
                user = cursor.fetchone()

                token = generate_token(user['password'], user['key'], session_id)
                if user and datetime.now() - user_session['active_time'] < timedelta(hours=4) and user_session['status'] == 1:
                    return User(session_id, user_session['username'], {1: 'admin', 2: 'staff'}.get(user_session['role']), token)
            else:
                return None
    except Exception as e:
        print(f"Load user error occurred: {e}")
        
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    role = ''
    invalidError = 'User not Found or Invalid Password. Please Try Again!'
    captchaError = 'To confirm that you’re a person and not a robot, solve the captcha.'
    error = invalidError
    
    try:
        if form.validate_on_submit():
            #setup variables from input fields
            username = request.form.get('username')
            password = request.form.get('password')
            role = request.form.get('role')
            input_captcha = request.form.get('captcha')
            form.captcha.data = ''
            user_role = {'1': 'admin', '2': 'staff'}.get(role, 'error')
            role = int(role)

            with config.conn.cursor() as cursor:
                #Search for the user in the database
                cursor.execute('SELECT * FROM user WHERE username = %s AND role = %s', (username, role,))
                user = cursor.fetchone()
                
                if captcha.get_answer() == input_captcha:#validate captcha input
                    if user and argon2.check_password_hash(user['password'], password) and user['status'] == 1:#authentication for login

                        session_id = generate_id()
                        cursor.execute('INSERT INTO session(session_id, user_id, username, role, status, active_time) VALUES (%s,%s,%s,%s,%s,NOW())', 
                                            (session_id, user['user_id'], username, role, 1))
                        config.conn.commit()
                        #generate token for session creation on cookies
                        token = generate_token(user['password'], user['key'], session_id)
                        login_user(User(session_id, username, user_role, token), remember=False)
                        
                        cursor.execute('UPDATE user SET online = 1, last_online = NULL WHERE user_id = %s', 
                                    (user['user_id'],))

                        redirect_url = {1: 'admin.dashboard', 2: 'staff.records'}.get(user['role'])#setup the role-based accessible pages
                        
                        if redirect_url:#redirect if user is authenicated and authorized
                            return redirect(url_for(redirect_url))
                        else:
                            error = invalidError
                    else:
                        error = invalidError
                else:
                    error = captchaError

    except Exception as e:
        print(f"log in occurred: {e}")

    return render_template('public/index.html', error_message=error, role = role, form=form)

@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    if current_user and current_user.is_authenticated and current_user.token:
        try:
            with config.conn.cursor() as cursor:
                cursor.execute('SELECT * FROM session WHERE session_id = %s', (current_user.id,))
                user_session = cursor.fetchone()

                if user_session:
                    cursor.execute('UPDATE user SET online = 0, last_online = NOW() WHERE user_id = %s', 
                                    (user_session['user_id'],))
                    cursor.execute('DELETE FROM session WHERE session_id = %s', (current_user.id,))
                    config.conn.commit()

        except Exception as e:
            print(f"Sign out error occurred: {e}")
        
        session.clear()
        logout_user()

    return redirect(url_for('home'))