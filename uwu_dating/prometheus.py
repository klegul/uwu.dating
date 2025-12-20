from flask import current_app
from flask_apscheduler import APScheduler
from prometheus_client import Gauge

from uwu_dating.db import count_users, count_messages, count_pokes, count_acked_pokes

lobby_current_connected = Gauge('uwu_dating_lobby_current_connected', 'Number of user in lobby')