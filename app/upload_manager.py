from flask import Blueprint, request, redirect, jsonify, url_for
from flask_login import login_required, current_user
from functools import wraps
from flask import current_app as app
from . import config 

upload_manager = Blueprint('upload_manager', __name__,url_prefix='/archival')

def authorization_requiered(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated and not current_user.is_active:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def newDocumentUploader(imageFile):

    document_id = ''
    
    return document_id

def linkStudent_documentTag(document_id, studentList):

    try:
        with config.conn.cursor() as cursor:



            queery_results ='success'

            return queery_results   

    except Exception as e:
            print(f"delete user error occurred: {e}")

@upload_manager.route('/archival/newRecord/document_upload', methods=['POST', 'GET'])
@login_required
def scanner():

    upload_result = 'failed'
    query_result = {'query_result': upload_result}
    return jsonify(query_result)