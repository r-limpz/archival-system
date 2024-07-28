from flask import Blueprint, request, redirect, render_template, jsonify, url_for
from flask_login import login_required
from app.secure.authorization import admin_required
from app.benchmark.accuracyChecker import benchmarkerTest
from app.benchmark.benchmark import updateCSV
import json

benchmark_manager = Blueprint('benchmark_manager', __name__,url_prefix='/admin/benchmark-manager/manage')

@benchmark_manager.route('/test_ocr/accuracy', methods=['POST', 'GET'])
@login_required
@admin_required
def testErrorRate():
    try:
        data = request.get_json()
        # Extract corrected_data and ocr_data from the JSON
        corrected_data = data.get('corrected_data')
        ocr_data = data.get('ocr_data')
        result = benchmarkerTest(corrected_data, ocr_data)

        if result:
            if updateCSV(result['average_WER'], result['average_WER'], "test.csv"):
                print(0)

            return jsonify(result)
        return None
    except Exception as e:
        print(f"Failed to reconnect: {e}")