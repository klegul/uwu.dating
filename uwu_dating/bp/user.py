import functools
import os
import re
from typing import List, Dict, Any

import requests
from flask import Blueprint, request, redirect, url_for, session, g, flash, render_template, abort

from markupsafe import escape

from uwu_dating.db import create_user, get_user, get_user_answers_for_questions, get_unacked_pokes, get_messages, \
    user_exists, delete_user
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
        if 'user' not in g or g.user is None:
            return redirect(url_for('welcome.index'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':

        name = escape(request.form.get('name'))
        dect = escape(request.form.get('dect'))
        meeting_point = escape(request.form.get('meeting_point'))

        error = None

        if not re.match(r'^\d{1,9}$', dect):
            error = 'Invalid DECT'

        if not name:
            error = 'Name is required'

        if not error:
            user = create_user(name, dect, meeting_point)

            session.clear()
            session.permanent = True
            session['user_id'] = user.id

            return redirect(url_for('question.answer', number=1))

        flash(error)

    return render_template('user/create.html')


@bp.route('/profile/<user_id>', methods=['GET'])
@user_required
def profile(user_id: str):
    if not user_exists(user_id):
        abort(400)

    g.profile_user = get_user(user_id)

    g.questions_answers = get_user_answers_for_questions(g.profile_user.id)

    g.user_score = round(get_user_score(g.user, g.profile_user) * 100)

    return render_template('user/profile.html')

@bp.route('/me', methods=['GET'])
@user_required
def me():
    pokes = get_unacked_pokes(g.user.id)
    template_pokes: List[Dict[str, Any]] = []
    for poke in pokes:
        poker = get_user(poke.poker_id)
        template_pokes.append({
            'id': poke.id,
            'poker_name': poker.name,
            'poker_id': poker.id
        })
    g.pokes = template_pokes

    messages = get_messages(g.user.id)
    template_message: List[Dict[str, Any]] = []
    for message in messages:
        sender = get_user(message.sender_id)
        template_message.append({
            'id': message.id,
            'sender_name': sender.name,
            'sender_id': sender.id,
            'content': message.content,
            'timestamp': message.timestamp,
        })
    g.messages = template_message

    g.questions_answers = get_user_answers_for_questions(g.user.id)

    return render_template('user/me.html')

@bp.route('/me/delete', methods=['GET'])
@user_required
def delete_me():
    delete_user(g.user.id)
    session.clear()

    return redirect(url_for('welcome'))

@bp.route('/report/<user_id>', methods=['GET'])
@user_required
def report(user_id: str):
    if not user_exists(user_id):
        abort(400)

    url = os.environ.get('REPORT_URL')
    requests.post(url, json={'reporter_id': g.user.id, "reported_id": user_id})

    return redirect(url_for('lobby.index'))
