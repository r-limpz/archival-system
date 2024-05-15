from flask import Blueprint,render_template, redirect, url_for
from functools import wraps
from flask_login import login_required, current_user

staff_bp = Blueprint('staff', __name__, url_prefix='/ards/staff')

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated and current_user.role != 'staff' or not current_user.is_active:
            return redirect(url_for('home'))
        elif current_user.is_authenticated and current_user.is_active and current_user.role == 'admin':
            return redirect(url_for('staff.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@staff_bp.route('/records')
@login_required
@staff_required
def records():
    return render_template('users/records.html')

@staff_bp.route('/documents')
@login_required
@staff_required
def documents():
    return render_template('users/documents.html')

@staff_bp.route('/upload')
@login_required
@staff_required
def upload():
    return render_template('users/upload.html')

@staff_bp.route('/account/<user>')
@staff_required
@login_required
def account(user):
    return render_template('users/account.html', user = user)
