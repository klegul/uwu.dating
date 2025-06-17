import sqlite3
from datetime import datetime
from typing import List, Dict, Any

import click
from flask import current_app, g

from uwu_dating.model import User, UserAnswer, Question


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def create_user(name: str, dect: str, meeting_point: str) -> User:
    db = get_db()
    db.execute('INSERT INTO user (name, dect, meeting_point) VALUES (?, ?, ?)', (name, dect, meeting_point))
    db.commit()

    user_id = db.execute('SELECT id FROM user WHERE name = ?', (name,)).fetchone()[0]
    return User(id=user_id, name=name, dect=dect, meeting_point=meeting_point)


def get_user(user_id: int) -> User:
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
    if user is None:
        raise Exception('User does not exist')
    return _parse_user(user)


def user_exists(user_id: int) -> bool:
    db = get_db()
    return db.execute('SELECT COUNT(*) FROM user WHERE id = ?', (user_id,)).fetchone()[0] > 0


def get_users() -> List[User]:
    db = get_db()
    users = db.execute('SELECT * FROM user').fetchall()
    result_list: List[User] = []
    for user in users:
        result_list.append(_parse_user(user))
    return result_list


def create_user_answer(user_id: int, question_number: int, answer: str) -> UserAnswer:
    db = get_db()
    db.execute('INSERT INTO user_answer VALUES (?, ?, ?)', (user_id, question_number, answer))
    db.commit()
    return UserAnswer(user_id=user_id, question_number=question_number, answer=answer)


def get_user_answers(user_id: int) -> List[UserAnswer]:
    db = get_db()
    answers = db.execute('SELECT * FROM user_answer WHERE user_id = ?', (user_id,)).fetchall()
    result_list: List[UserAnswer] = []
    for answer in answers:
        result_list.append(_parse_user_answer(answer))
    return result_list


def get_question(number: int) -> Question:
    db = get_db()
    question = db.execute('SELECT * FROM question WHERE number = ?', (number,)).fetchone()
    if question is None:
        raise Exception('No such question')
    return _parse_question(question)


def get_user_answers_for_questions(user_id: int) -> Dict[Question, UserAnswer]:
    db = get_db()
    user_answers = db.execute('SELECT * FROM user_answer WHERE user_id = ? ORDER BY question_number',
                              (user_id,)).fetchall()
    questions = db.execute('SELECT * FROM question ORDER BY number').fetchall()
    result_dict: Dict[Question, UserAnswer] = {}
    for db_question, db_user_answers in zip(questions, user_answers):
        result_dict[_parse_question(db_question)] = _parse_user_answer(db_user_answers)
    return result_dict


def _parse_user(db_user: Dict[str, Any]) -> User:
    return User(id=db_user['id'], name=db_user['name'], dect=db_user['dect'], meeting_point=db_user['meeting_point'])


def _parse_question(db_question: Dict[str, Any]) -> Question:
    return Question(number=db_question['number'], question=db_question['question'], type=db_question['type'],
                    submit_label=db_question['submit_label'])


def _parse_user_answer(db_answer: Dict[str, Any]) -> UserAnswer:
    return UserAnswer(question_number=db_answer['question_number'], user_id=db_answer['user_id'],
                      answer=db_answer['answer'])


def count_questions() -> int:
    db = get_db()
    return db.execute('SELECT COUNT(*) FROM question').fetchone()[0]
