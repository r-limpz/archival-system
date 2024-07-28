from flask import Blueprint, request, redirect, render_template, jsonify, url_for
from flask_login import login_required
from app.secure.authorization import admin_required
from app.benchmark.benchmark import getAccuracy
from app.benchmark.accuracyChecker import checkMissingData

benchhmark_manager = Blueprint('benchhmark_manager', __name__,url_prefix='/admin/benchmark-manager/manage')

@benchhmark_manager.route('/test_ocr/accuracy', methods=['POST'])
@login_required
@admin_required
def testErrorRate():
    if request.method == "POST":
        data = request.get_json()
        corrected_data = data.get('corrected_data')
        ocr_data = data.get('ocr_data')

        data = checkMissingData(corrected_data, ocr_data)
        filename = "test.csv"
        if data:
            if getAccuracy(data['average_WER'], data['average_CER'], filename):
                return render_template ('admin/results.html', average_WER = data['average_WER'], average_CER = data['average_CER'])

@benchhmark_manager.route('/fetch_data/accuracy', methods=['POST'])
@login_required
@admin_required
def fetchCSV():
    return None