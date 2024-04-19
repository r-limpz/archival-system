from flask import Flask, session, render_template, redirect, url_for, request, flash, jsonify, json
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_argon2 import Argon2
from flask_session_captcha import FlaskSessionCaptcha
from . import config
from app.Blueprints.admin import admin_bp
from app.Blueprints.staff import staff_bp
from datetime import datetime, timedelta

# Create Flask app
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = "ABCDEFG12345"
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=20)

app.config['CAPTCHA_ENABLE'] = True 
app.config['CAPTCHA_LENGTH'] = 6
app.config['CAPTCHA_WIDTH'] = 200
app.config['CAPTCHA_HEIGHT'] = 60
captcha = FlaskSessionCaptcha(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.refresh_view = 'index'
login_manager.login_view = 'login'

csrf = CSRFProtect() 
csrf.init_app(app)

argon2 = Argon2(app)
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.user = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    cursor = config.conn.cursor()
    cursor.execute('SELECT * FROM user WHERE user_id = %s', (user_id,))
    user = cursor.fetchone()

    select_role = {1: 'admin', 2: 'staff'}
    role = select_role.get(user['role'])
        
    return User(user_id, user['username'], role)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('1', 'Admin'), ('2', 'Staff')], validators=[DataRequired()])
    captcha = StringField('Captcha', validators=[DataRequired()])
    submit = SubmitField('Sign In')

#Login route
@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    role = ''
    invalidError = 'User not Found or Invalid Password - Please Try Again'
    
    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        input_captcha = request.form.get('captcha')

        role_dict = {1: 'admin', 2: 'staff'}
        user_role = role_dict.get(role, 'error')

        #authentication for login
        cursor = config.conn.cursor()
        cursor.execute('SELECT * FROM user WHERE username = %s AND role = %s', (username, role,))
        user = cursor.fetchone()
    
        if captcha.get_answer() == input_captcha:
            if user and argon2.check_password_hash(user['password'], password) and user['status'] == 1:
                    
                login_user(User(user['user_id'], username, user_role), remember=False)#add user info on session
                session.permanent = True

                #login logs
                browser_uuid = request.headers.get('User-Agent')
                cursor.execute('INSERT INTO login_history (user_id, browser_uuid) VALUES (%s, %s)', (user['user_id'], browser_uuid))
                config.conn.commit()

                role_redirect = {1: 'admin.dashboard', 2: 'staff.records'}
                redirect_url = role_redirect.get(user['role'])

                if redirect_url:
                    return redirect(url_for(redirect_url))
                else:
                    flash(invalidError)
            else:
                flash(invalidError)
        else:
            flash('Please be a human!')
            
    return render_template('public/index.html', error_message=invalidError, role = role, form=form)

#Logout route
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    cursor = config.conn.cursor()
    cursor.execute('UPDATE login_history SET logout_time = NOW() WHERE user_id = %s AND logout_time IS NULL', (current_user.id,))
    config.conn.commit()
    logout_user()
    flash('Account Logged Out')
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('errors/500.html'), 500

#Register blueprints for Admin pages and Staff pages
app.register_blueprint(admin_bp)
app.register_blueprint(staff_bp)

#Account page route
@app.route('/account')
@login_required
def account():
    
    role_redirect = {'admin': 'admin.account', 'staff': 'staff.account'}
    redirect_url = role_redirect.get(current_user.role)
    return redirect(url_for(redirect_url, user = current_user.user))

#Records page route
@app.route('/records')
@login_required
def records():
    
    role_redirect = {'admin': 'admin.records', 'staff': 'staff.records'}
    redirect_url = role_redirect.get(current_user.role)
    return redirect(url_for(redirect_url))

#Documents page route
@app.route('/documents')
@login_required
def documents():
    
    role_redirect = {'admin': 'admin.documents', 'staff': 'staff.documents'}
    redirect_url = role_redirect.get(current_user.role)
    return redirect(url_for(redirect_url))

#Upload page route
@app.route('/upload')
@login_required
def upload():
    return redirect(url_for('staff.upload'))

#Dashboard page route
@app.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('admin.dashboard'))

#Account Manager page route
@app.route('/account_manager')
@login_required
def account_manager():
    return redirect(url_for('admin.account_manager'))

#Collage and Course Manager page route
@app.route('/col_course_manager')
@login_required
def col_course_manager():
    return redirect(url_for('admin.col_course_manager'))

@app.route('/ards/')
def index():
    return redirect(url_for('home'))

@app.route('/ards')
def home():
    form = LoginForm()
    return render_template('public/index.html', form=form)

@app.route('/records_data', methods=['GET', 'POST'])
def records_data():
    cursor = config.conn.cursor()
    
    if request.method =='POST':
        
        draw = request.form['draw']
        row = int(request.form['start'])
        rowperpage = int(request.form['length'])
        column_index = request.form['order[0][column]']
        sort_direction = request.form['order[0][dir]']
        searchValue = request.form['search[value]']
        
        likeString = "%" + searchValue + "%"
        
        # Total count data
        cursor.execute('SELECT COUNT(*) AS ALLCOUNT FROM srecordstbl' )
        rsallcounts = cursor.fetchone()
        totalRecords = rsallcounts['ALLCOUNT']
        
        # Total count with filter
        cursor.execute('SELECT COUNT(*) AS ALLCOUNT FROM srecordstbl WHERE FullName LIKE %s OR College LIKE %s OR Course LIKE %s OR year_level LIKE %s OR Subject LIKE %s OR Semester LIKE %s OR SchoolYear LIKE %s', (likeString, likeString, likeString, likeString, likeString, likeString, likeString))
        rsallcounts = cursor.fetchone()
        totalRecordswFilter = rsallcounts['ALLCOUNT']
        
        # feth all data records
        if searchValue == '':   
            cursor.execute(f'SELECT * FROM srecordstbl ORDER BY {column_index} {sort_direction} LIMIT %s, %s;', (row, rowperpage))
            student_records = cursor.fetchall()
        else:
            cursor.execute(f'SELECT * FROM srecordstbl WHERE FullName LIKE %s OR College LIKE %s OR Course LIKE %s OR year_level LIKE %s OR Subject LIKE %s OR Semester LIKE %s OR SchoolYear LIKE %s ORDER BY {column_index} {sort_direction} LIMIT %s, %s;', (likeString, likeString, likeString, likeString, likeString, likeString, likeString, row, rowperpage))
            student_records = cursor.fetchall()

        # Convert your data to a format that DataTables can read
        data = []
        for row in student_records:
            data.append({ 
                         'id' : row['id'],
                         'FullName' : row['FullName'],
                         'College' : row['College'],
                         'Course' : row['Course'],
                         'year_level' : row['year_level'],
                         'Subject' : row['Subject'],
                         'Semester' : row['Semester'],
                         'SchoolYear' : row['SchoolYear'] 
                         })

        response = {
            'draw': draw,
            'iTotalRecords': totalRecords,
            'iTotalDisplayRecords': totalRecordswFilter,
            'aaData': data,
            }

        return jsonify(response)

