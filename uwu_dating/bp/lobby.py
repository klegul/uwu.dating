from typing import Dict

from flask import render_template, request, Blueprint, g
from flask_socketio import emit, SocketIO

from uwu_dating.bp.user import user_required
from uwu_dating.db import user_exists, get_user, count_unacked_pokes, count_user_messages, get_unacked_pokes
from uwu_dating.prometheus import lobby_current_connected
from uwu_dating.utils import get_user_score

bp = Blueprint('lobby', __name__)

lobby_socket = SocketIO(async_mode="gevent")
users: Dict[str, str] = {}


@bp.route('/', methods=['GET'])
@user_required
def index():
    _update_unacked_pokes_messages(g.user.id)
    return render_template('lobby.html')


@lobby_socket.on('hello')
def handle_join(user_id):
    if not user_exists(user_id):
        raise Exception('User not found')

    users[request.sid] = user_id

    lobby_current_connected.inc(1)

    for sid, for_user_id in users.items():
        for_user = get_user(for_user_id)
        for other_user_id in users.values():
            if other_user_id == for_user_id:
                continue
            other_user = get_user(other_user_id)
            emit('join', {
                'id': other_user.id,
                'name': other_user.name,
                'score': get_user_score(for_user, other_user)
            }, to=sid)

@lobby_socket.on('disconnect')
def handle_disconnect():
    user_id = users[request.sid]
    users.pop(request.sid)
    emit('leave', {'id': user_id}, broadcast=True)

    lobby_current_connected.dec(1)

@lobby_socket.on('update')
def handle_update():
    user_id = users[request.sid]
    _update_unacked_pokes_messages(user_id)
    emit('update', {'unacked_pokes': g.unacked_pokes, 'messages': g.messages}, broadcast=False)

def _update_unacked_pokes_messages(user_id: str):
    g.unacked_pokes = count_unacked_pokes(user_id)
    g.messages = count_user_messages(user_id)