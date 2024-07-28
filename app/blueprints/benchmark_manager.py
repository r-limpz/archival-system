from flask import Blueprint, request, redirect, render_template, jsonify, url_for
from flask import current_app as app
from app.secure.authorization import admin_required

benchhmark_manager = Blueprint('benchhmark_manager', __name__,url_prefix='/admin/benchmark-manager/manage/ocr_tool')