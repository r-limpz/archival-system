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
from app.Blueprints.ocr import ocr_bp
from datetime import timedelta
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import os
import re
import json

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

app.config['UPLOAD_FOLDER'] = os.path.realpath('app/static')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


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
    role = SelectField('Role', choices=[('2', 'Staff'), ('1', 'Admin')], validators=[DataRequired()])
    captcha = StringField('Captcha', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class StudentNames:
    def __init__(self, surname, firstname, middlename, suffix):
        self.surname = surname
        self.firstname = firstname
        self.middlename = middlename
        self.suffix = suffix

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

        role_dict = {'1': 'admin', '2': 'staff'}
        user_role = role_dict.get(role, 'error')
        role = int(role)

        #authentication for login
        cursor = config.conn.cursor()
        cursor.execute('SELECT * FROM user WHERE username = %s AND role = %s', (username, role,))
        user = cursor.fetchone()
        print(username , role)
        print(user)
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
app.register_blueprint(ocr_bp)
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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def removeUnwantedCharacters(raw_inputArray):
    filtered_studentNames = [
        re.sub(r'\s+', ' ', re.sub(r',', ' , ', re.sub(r'[^a-zA-ZÑñ.,]', ' ', rawText))).strip().lower()
        for rawText in raw_inputArray
    ]
    return filtered_studentNames

def isSuffixAndMiddleName(unstructured_ListOfSplitName):
    suffixList = ['jr.', 'sr.', 'i.', 'ii.', 'iii.', 'iv.', 'v.']
    data = {'middlename': '', 'middlename_index': -1, 'suffix': '', 'suffix_index': -1}
    for i, name in enumerate(unstructured_ListOfSplitName):
        if len(name) == 2 and name[1] == '.':
            data['middlename'] = name
            data['middlename_index'] = i
    for i in range(len(unstructured_ListOfSplitName)-1, -1, -1):
        if unstructured_ListOfSplitName[i] in suffixList and i != data['middlename_index']:
            data['suffix'] = unstructured_ListOfSplitName[i]
            data['suffix_index'] = i
    return data

def detectNameFormat(unstructured_nameformat):
    #setup the format and variables
    structured_nameformat = { 'surname': '', 'firstname': '', 'middlename': '', 'suffix': '' }
    array_name = unstructured_nameformat.split() #spli each by combination of characters/words
    nameData = isSuffixAndMiddleName(array_name) #run the function to get both middlename and suffix
    structured_nameformat['middlename'] = nameData.get('middlename').capitalize()# Add middleName
    middleNameIndex = nameData.get('middlename_index')
    structured_nameformat['suffix'] = nameData.get('suffix').upper()# Add suffix
    suffixIndex = nameData.get('suffix_index')
    temp_firstname = ''
    temp_surname = ''

    if not suffixIndex == -1: #after the suffix string value is stored remove it to the temporary list
        array_name = array_name[:suffixIndex] + array_name[suffixIndex+1:]
    
    #Determine if a comma is present to separate surname and firstname
    comma_index = array_name.index(',') if ',' in array_name else None

    if comma_index is not None: # f format is [ SURNAME* + ,+ FIRSTNAME* + M.I ]
        if not middleNameIndex == -1: #remove it since the structure doesn't relies on middlename location
            array_name = array_name[:middleNameIndex] + array_name[middleNameIndex+1:] #remove the middleName from the list
        
        temp_surname =  ' '.join(array_name[:comma_index]).title() #all list before comma is surname
        temp_firstname =  ' '.join(array_name[comma_index+1:]).title() #all list after comma is firstname
        
    else: #if format is [ FIRSTNAME* + M.I + SURNAME* ]
        if not middleNameIndex == -1 : #Has MiddleName
            if middleNameIndex == len(array_name):
                for i in range(len(array_name)-1, -1, -1):
                    if len(array_name[i]) > 1 and '.' not in array_name[i]:
                        temp_surname = array_name[i].upper()+'.'
                        array_name = array_name[:i] + array_name[i+1:]
                        break
                array_name = array_name[:middleNameIndex] + array_name[middleNameIndex+1:]
                temp_firstname = ' '.join(array_name[:len(array_name)-1])
            else:
                temp_firstname = ' '.join(array_name[:middleNameIndex]) #all list before middlename is firstname
                temp_surname = ' '.join(array_name[middleNameIndex+1:]) #all list after middlename is surname

            array_name = array_name[:middleNameIndex] + array_name[middleNameIndex+1:]
            
        else: # [FIRSTNAME* + SURNAME]
            for i in range(len(array_name)-1, -1, -1): #locate the middlename
                if len(array_name[i]) == 1:
                    structured_nameformat['middlename'] = array_name[i].upper()+'.'
                    break

            for i in range(len(array_name)-1, -1, -1):
                if len(array_name[i]) > 1 and '.' not in array_name[i]:
                    temp_surname = array_name[i].upper()+'.'
                    array_name = array_name[:i] + array_name[i+1:]
                    break

            temp_firstname = ' '.join(array_name[:len(array_name)-1])

    # add the values for the structured name format dictionary for surname and firstname
    structured_nameformat['surname'] = re.sub(r',', '', re.sub(r'[^a-zA-ZÑñ]', ' ', temp_surname)).title()
    structured_nameformat['firstname'] = re.sub(r',', '', re.sub(r'[^a-zA-ZÑñ.]', ' ', temp_firstname)).title()

    return structured_nameformat

def detectStudentNames(raw_data_string):
    StudentNamesList = []
    temp_studentList = []

    filteredData = removeUnwantedCharacters(raw_data_string)
    for input_name in filteredData:
        if input_name !='':
            name_result = detectNameFormat(input_name)
            student_data = StudentNames(**name_result)
            temp_studentList.append(student_data)
    
    for obj in temp_studentList: #append and remove redundancy
        if not obj.surname == '' and not obj.firstname == '' and not any(o.surname == obj.surname and o.firstname == obj.firstname and o.middlename == obj.middlename and o.suffix == obj.suffix for o in StudentNamesList):
            StudentNamesList.append(obj)
    
    return StudentNamesList

@app.route('/scanner', methods=['POST'])
@login_required
def scanner():
    if 'image' not in request.files:
        return "No file uploaded"
    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        return "No file selected or unsupported file type"

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file.save(filepath)

    try:
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img)
        raw_names = text.split('\n')
        students = detectStudentNames(raw_names)
        # Convert the list of student objects to JSON
        students_json = [student.__dict__ for student in students]
    except Exception as e:
        os.remove(filepath)  # Clean up the file if something goes wrong
        return f"An error occurred: {str(e)}"

    return render_template('users/result.html', students_json=students_json)