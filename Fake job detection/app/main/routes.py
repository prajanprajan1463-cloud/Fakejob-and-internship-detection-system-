from flask import render_template, redirect, url_for
from app.main import main_bp


@main_bp.route('/')
def index():
    return render_template('main/index.html')


@main_bp.route('/dashboard')
def dashboard_redirect():
    return redirect(url_for('analysis.dashboard'))


@main_bp.route('/how-it-works')
def how_it_works():
    return render_template('main/how_it_works.html')



@main_bp.route('/safety-tips')
def safety_tips():
    return render_template('main/safety_tips.html')
