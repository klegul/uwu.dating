from typing import List, Dict

from flask import Blueprint, request, render_template, g, redirect, url_for
from markupsafe import escape

from uwu_dating.db import create_user_answer, count_questions, get_question, get_answer_choices
from uwu_dating.bp.user import user_required
from uwu_dating.model import AnswerChoice

bp = Blueprint('question', __name__, url_prefix='/question')


@bp.route('/answer/<int:number>', methods=['POST', 'GET'])
@user_required
def answer(number: int):
    g.question = get_question(number)
    if request.method == 'POST':
        answer_text = escape(request.form['answer'])

        create_user_answer(g.user.id, number, answer_text)

        if count_questions() >= number + 1:
            return redirect(url_for('question.answer', number=number + 1))
        return redirect(url_for('lobby.index'))
    else:
        answer_choices = get_answer_choices()
        template_answer_choices: Dict[int, List[AnswerChoice]] = {}
        for answer_choice in answer_choices:
            if answer_choice.question_number not in template_answer_choices:
                template_answer_choices[answer_choice.question_number] = []
            template_answer_choices[answer_choice.question_number].append(answer_choice)
        g.answer_choices = template_answer_choices

        return render_template('question.html')
