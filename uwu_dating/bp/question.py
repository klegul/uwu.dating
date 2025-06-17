from flask import Blueprint, request, render_template, g, redirect, url_for

from uwu_dating.db import create_user_answer, count_questions, get_question
from uwu_dating.bp.user import user_required

bp = Blueprint('question', __name__, url_prefix='/question')


@bp.route('/answer/<int:number>', methods=['POST', 'GET'])
@user_required
def answer(number: int):
    g.question = get_question(number)
    if request.method == 'POST':
        answer_text = request.form['answer']

        create_user_answer(g.user.id, number, answer_text)

        if count_questions() >= number + 1:
            return redirect(url_for('question.answer', number=number + 1))
        return redirect(url_for('lobby.index'))
    else:
        return render_template('question.html')
