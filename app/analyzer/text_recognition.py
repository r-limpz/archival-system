from flask import current_app as app
from flask import jsonify
import pytesseract
from PIL import Image
from app.analyzer.name_formatter import detectStudentNames

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def ocr_scanner(filepath):
    if filepath == '' or not allowed_file(filepath):
        return "Unsupported file type. Please provide a valid image file."

    try:
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img)
        raw_names = text.split('\n')
        students = detectStudentNames(raw_names)  # Assuming detectStudentNames is defined elsewhere
        
        return students
        
    except Exception as e:
        return jsonify({'error': str(e)})
