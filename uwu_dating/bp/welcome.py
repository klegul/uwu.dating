from flask import Blueprint, render_template

bp = Blueprint('welcome', __name__, url_prefix='/welcome')

@bp.route('/', methods=['GET'])
def index():
    return render_template('welcome.html')

