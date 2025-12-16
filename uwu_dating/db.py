import os
import sqlite3
import time
import uuid
from datetime import datetime
from typing import List, Dict, Any

import click
from click import Choice
from flask import current_app, g

from uwu_dating.model import User, UserAnswer, Question, Poke, Message, AnswerChoice


def get_db():
    if 'db' not in g:
        if not os.path.exists(current_app.config['DATABASE']):
            open(current_app.config['DATABASE'], 'x').close()
            db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            init_db(db)

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


def init_db(db: sqlite3.Connection):
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    with current_app.open_resource('questions.sql') as f:
        db.executescript(f.read().decode('utf8'))


sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)


def init_app(app):
    app.teardown_appcontext(close_db)


def create_user(name: str, dect: str, meeting_point: str) -> User:
    db = get_db()
    user_id = str(uuid.uuid4())
    db.execute('INSERT INTO user (id, name, dect, meeting_point) VALUES (?, ?, ?, ?)',
               (user_id, name, dect, meeting_point))
    db.commit()

    return User(id=user_id, name=name, dect=dect, meeting_point=meeting_point)


def get_user(user_id: str) -> User:
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
    if user is None:
        raise Exception('User does not exist')
    return _parse_user(user)


def user_exists(user_id: str) -> bool:
    db = get_db()
    return db.execute('SELECT COUNT(*) FROM user WHERE id = ?', (user_id,)).fetchone()[0] > 0


def get_users() -> List[User]:
    db = get_db()
    users = db.execute('SELECT * FROM user').fetchall()
    result_list: List[User] = []
    for user in users:
        result_list.append(_parse_user(user))
    return result_list


def count_users() -> int:
    db = get_db()
    return db.execute('SELECT COUNT(*) FROM user').fetchone()[0]


def create_user_answer(user_id: str, question_number: int, answer: str) -> UserAnswer:
    db = get_db()

    count = db.execute('SELECT COUNT(*) FROM user_answer WHERE user_id = ? and question_number = ?',
                       (user_id, question_number)).fetchone()[0]
    if count > 0:
        db.execute('DELETE FROM user_answer WHERE user_id = ? and question_number = ?', (user_id, question_number))

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


def get_user_answers_for_questions(user_id: str) -> Dict[Question, UserAnswer]:
    db = get_db()
    user_answers = db.execute('SELECT * FROM user_answer WHERE user_id = ? ORDER BY question_number',
                              (user_id,)).fetchall()
    questions = db.execute('SELECT * FROM question ORDER BY number').fetchall()
    result_dict: Dict[Question, UserAnswer] = {}
    for db_question, db_user_answers in zip(questions, user_answers):
        result_dict[_parse_question(db_question)] = _parse_user_answer(db_user_answers)
    return result_dict


def count_questions() -> int:
    db = get_db()
    return db.execute('SELECT COUNT(*) FROM question').fetchone()[0]


def get_answer_choices() -> List[AnswerChoice]:
    db = get_db()
    answer_choices = db.execute('SELECT * FROM answer_choice ORDER BY number').fetchall()
    result_list: List[AnswerChoice] = []
    for answer_choice in answer_choices:
        result_list.append(_parse_answer_choice(answer_choice))
    return result_list


def create_poke(poker_id: str, poked_id: str) -> Poke:
    db = get_db()
    poke_id = str(uuid.uuid4())
    db.execute('INSERT INTO poke (id, poker_id, poked_id, acked) VALUES (?, ?, ?, ?)', (poke_id, poker_id, poked_id, 0))
    db.commit()
    return Poke(id=poke_id, poker_id=poker_id, poked_id=poked_id, acked=False)


def get_unacked_pokes(poked_id: str) -> List[Poke]:
    db = get_db()
    pokes = db.execute('SELECT * FROM poke WHERE poked_id = ? AND acked = 0', (poked_id,)).fetchall()
    result_list: List[Poke] = []
    for poke in pokes:
        result_list.append(_parse_poke(poke))
    return result_list


def get_poke(poke_id: str) -> Poke:
    db = get_db()
    poke = db.execute('SELECT * FROM poke WHERE id = ?', (poke_id,)).fetchone()
    if poke is None:
        raise Exception('No such poke')
    return _parse_poke(poke)


def ack_poke(poke_id: str) -> None:
    db = get_db()
    db.execute('UPDATE poke SET acked = ? WHERE id = ?', (True, poke_id))
    db.commit()


def count_pokes() -> int:
    db = get_db()
    return db.execute('SELECT COUNT(*) FROM poke').fetchone()[0]


def count_acked_pokes() -> int:
    db = get_db()
    return db.execute('SELECT COUNT(*) FROM poke WHERE acked = 1').fetchone()[0]


def count_unacked_pokes(user_id: str) -> int:
    db = get_db()
    return db.execute('SELECT COUNT(*) FROM poke WHERE acked = 0 AND poked_id = ?', (user_id,)).fetchone()[0]


def create_message(sender_id: str, recipient_id: str, content: str) -> Message:
    db = get_db()
    timestamp = int(time.time())
    message_id = str(uuid.uuid4())
    db.execute('INSERT INTO message (id, sender_id, recipient_id, content, timestamp) VALUES (?, ?, ?, ?, ?)',
               (message_id, sender_id, recipient_id, content, timestamp))
    db.commit()
    return Message(id=message_id, sender_id=sender_id, recipient_id=recipient_id, content=content, timestamp=timestamp)


def get_messages(recipient_id: str) -> List[Message]:
    db = get_db()
    messages = db.execute('SELECT * FROM message WHERE recipient_id = ?', (recipient_id,)).fetchall()
    result_list: List[Message] = []
    for message in messages:
        result_list.append(_parse_message(message))
    return result_list


def delete_message(message_id: str) -> None:
    db = get_db()
    db.execute('DELETE FROM message WHERE id = ?', (message_id,))
    db.commit()


def count_messages() -> int:
    db = get_db()
    return db.execute('SELECT COUNT(*) FROM message').fetchone()[0]


def count_user_messages(user_id: str) -> int:
    db = get_db()
    return db.execute('SELECT COUNT(*) FROM message WHERE recipient_id = ?', (user_id,)).fetchone()[0]


def _parse_user(db_user: Dict[str, Any]) -> User:
    return User(id=db_user['id'], name=db_user['name'], dect=db_user['dect'], meeting_point=db_user['meeting_point'])


def _parse_question(db_question: Dict[str, Any]) -> Question:
    return Question(number=db_question['number'], question=db_question['question'], type=db_question['type'],
                    submit_label=db_question['submit_label'])


def _parse_answer_choice(db_answer_choice: Dict[str, Any]) -> AnswerChoice:
    return AnswerChoice(question_number=db_answer_choice['question_number'], number=db_answer_choice['number'],
                        answer=db_answer_choice['answer'])


def _parse_poke(db_poke: Dict[str, Any]) -> Poke:
    return Poke(id=db_poke['id'], poker_id=db_poke['poker_id'], poked_id=db_poke['poked_id'],
                acked=bool(db_poke['acked']))


def _parse_message(message: Dict[str, Any]) -> Message:
    return Message(id=message['id'], sender_id=message['sender_id'], recipient_id=message['recipient_id'],
                   content=message['content'], timestamp=message['timestamp'])


def _parse_user_answer(db_answer: Dict[str, Any]) -> UserAnswer:
    return UserAnswer(question_number=db_answer['question_number'], user_id=db_answer['user_id'],
                      answer=db_answer['answer'])
