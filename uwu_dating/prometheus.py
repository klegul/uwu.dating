from flask import current_app
from flask_apscheduler import APScheduler
from prometheus_client import Gauge

from uwu_dating.db import count_users, count_messages, count_pokes, count_acked_pokes

lobby_current_connected = Gauge('lobby_current_connected', 'Number of user in lobby')
user_count = Gauge('user_count', 'Number of users')
messages_count = Gauge('messages_count', 'Number of messages')
pokes_cont = Gauge('pokes_cont', 'Number of pokes')
pokes_acked = Gauge('pokes_acked', 'Number of pokes acked')

scheduler = APScheduler()

@scheduler.task('interval', minutes=1)
def background_task():
    with current_app.app_context():
        user_count.set(count_users())
        messages_count.set(count_messages())
        pokes_cont.set(count_pokes())
        pokes_acked.set(count_acked_pokes())

def init_scheduler(app):
    with app.app_context():
        scheduler.init_app(app)
        scheduler.start()
        scheduler.add_job(id='scheduled_task', func=background_task, trigger='interval', minutes=1)