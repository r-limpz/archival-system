from flask import Blueprint,render_template, redirect, url_for
from functools import wraps
from flask_login import login_required, logout_user, current_user

admin_bp = Blueprint('admin', __name__, url_prefix='/ards/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    return render_template('users/dashboard.html')

@admin_bp.route('/records')
@login_required
@admin_required
def records():
    return render_template('users/records.html')

@admin_bp.route('/documents')
@login_required
@admin_required
def documents():
    return render_template('users/documents.html')

@admin_bp.route('/account_manager')
@login_required
@admin_required
def account_manager():
    return render_template('users/user_control.html')

@admin_bp.route('/collage&course_manager')
@login_required
@admin_required
def col_course_manager():
    return render_template('users/colcourse.html')

@admin_bp.route('/<user>')
@login_required
@admin_required
def account(user):
    return render_template('users/account.html', user = user)