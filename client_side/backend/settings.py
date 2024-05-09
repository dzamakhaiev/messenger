
from helpers.network import find_free_port

LISTENER_HOST = '127.0.0.1'
LISTENER_PORT = find_free_port()
LISTENER_URL = f'http://{LISTENER_HOST}:{LISTENER_PORT}'
