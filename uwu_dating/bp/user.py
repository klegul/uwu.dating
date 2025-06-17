import functools

from flask import Blueprint, request, redirect, url_for, session, g, flash, render_template

from uwu_dating.db import create_user, get_user, get_user_answers_for_questions
from uwu_dating.utils import get_user_score

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        try:
            g.user = get_user(user_id)
        except Exception:
            pass

def user_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('user.create'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':

        name = request.form.get('name')
        dect = request.form.get('dect')
        meeting_point = request.form.get('meeting_point')

        error = None

        if not name:
            error = 'Name is required'

        if not error:
            user = create_user(name, dect, meeting_point)

            session.clear()
            session['user_id'] = user.id

            return redirect(url_for('question.answer', number=1))

        flash(error)

    return render_template('user/create.html')

@bp.route('/profile/<int:id>', methods=['GET'])
@user_required
def profile(id: int):
    g.profile_user = get_user(id)

    g.questions_answers = get_user_answers_for_questions(g.profile_user.id)

    g.user_score = get_user_score(g.user, g.profile_user)

    return render_template('user/profile.html')
