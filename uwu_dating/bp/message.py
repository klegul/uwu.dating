from flask import Blueprint, request, g, redirect, url_for, render_template

from uwu_dating.bp.lobby import lobby_socket
from uwu_dating.bp import lobby
from uwu_dating.bp.user import user_required
from uwu_dating.db import create_message, get_user, delete_message

bp = Blueprint('message', __name__, url_prefix='/message')

@bp.route('/send/<recipient_id>', methods=['GET', 'POST'])
@user_required
def send(recipient_id: str):
    if request.method == 'POST':
        content = request.form['content']

        create_message(g.user.id, recipient_id, content)

        user_sid = None
        for sid, user_user_id in lobby.users.items():
            if user_user_id == recipient_id:
                user_sid = sid

        lobby_socket.emit('message', to=user_sid)

        return redirect(url_for('user.profile', user_id=recipient_id))

    g.recipient = get_user(recipient_id)

    return render_template('message.html')

@bp.route('/delete/<message_id>', methods=['GET'])
@user_required
def delete(message_id: str):
    delete_message(message_id)

    return redirect(url_for('user.me'))