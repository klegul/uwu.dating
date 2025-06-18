from prometheus_client import Gauge

lobby_current_connected = Gauge('lobby_current_connected', 'Number of user in lobby')
