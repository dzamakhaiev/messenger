from helpers.network import find_free_port

LISTENER_HOST = 'localhost'
LISTENER_PORT = find_free_port()
LISTENER_URL = f'http://{LISTENER_HOST}:{LISTENER_PORT}'
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FORMAT = "%(asctime)s %(levelname)s %(module)s: %(message)s"
