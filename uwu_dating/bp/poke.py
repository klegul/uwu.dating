from flask import Blueprint, g, url_for, redirect, abort

from uwu_dating.bp.lobby import lobby_socket
from uwu_dating.bp import lobby
from uwu_dating.bp.user import user_required
from uwu_dating.db import create_poke, get_poke, ack_poke, user_exists, poke_exists

bp = Blueprint('poke', __name__, url_prefix='/poke')

@bp.route('/poke/<user_id>', methods=['GET'])
@user_required
def poke(user_id: str):
    if not user_exists(user_id):
        abort(400)

    create_poke(g.user.id, user_id)

    user_sid = None
    for sid, user_user_id in lobby.users.items():
        if user_user_id == user_id:
            user_sid = sid

    lobby_socket.emit('poke', to=user_sid)

    return redirect(url_for('lobby.index'))

@bp.route('/ack/<poke_id>', methods=['GET'])
@user_required
def ack(poke_id: str):
    if not poke_exists(poke_id):
        abort(400)

    poke = get_poke(poke_id)
    if poke.poked_id != g.user.id:
        return 'Please do not do evil things :c'

    ack_poke(poke_id)
    return redirect(url_for('user.me'))

