from flask import current_app as app
from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.analyzer.detectTable import CropTable
from app.analyzer.text_recognition import ocr_scanner

ocr_App = Blueprint('ocr', __name__)

class StudentNames:
    def __init__(self, surname, firstname, middlename, suffix):
        self.surname = surname
        self.firstname = firstname
        self.middlename = middlename
        self.suffix = suffix

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@ocr_App.route('/scanner', methods=['POST'])
@login_required
def scanner():

    if 'document_image' not in request.files:
            return "No file uploaded"
    
    file = request.files['document_image']
    
    if file.filename == '' or not allowed_file(file.filename):
            return "No file selected or unsupported file type"
    
    try:
        crop_image = CropTable(file)
        if crop_image:
            students = ocr_scanner(crop_image)
            
            return jsonify([student.__dict__ for student in students])
        
    except Exception as e:
        return jsonify(e)
