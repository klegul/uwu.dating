from typing import List, Dict

from flask import render_template, request, Blueprint
from flask_socketio import emit, SocketIO

from uwu_dating.bp.user import user_required
from uwu_dating.db import user_exists, get_user
from uwu_dating.utils import get_user_score

bp = Blueprint('lobby', __name__)

lobby_socket = SocketIO()
users: Dict[str, str] = {}


@bp.route('/', methods=['GET'])
@user_required
def index():
    return render_template('lobby.html')


@lobby_socket.on('join')
def handle_join(user_id):
    if not user_exists(user_id):
        raise Exception('User not found')

    users[request.sid] = user_id

    for sid, for_user_id in users.items():
        for_user = get_user(int(for_user_id))
        for other_user_id in users.values():
            if other_user_id == for_user_id:
                continue
            other_user = get_user(int(other_user_id))
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