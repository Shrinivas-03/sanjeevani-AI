from flask import Blueprint, render_template

# Change the blueprint name from 'functionality' to 'func' to match app registration
func_bp = Blueprint('func', __name__, template_folder='../templates')

@func_bp.route('/dashboard')
def dashboard():
    return render_template('dash.html')

@func_bp.route('/profile')
def profile():
    return render_template('profile.html')

@func_bp.route('/prediction_history')
def prediction_history():
    return render_template('prediction_history.html')