from server_side.app.settings import REST_API_HOST, REST_API_PORT
from helpers.network import find_free_port

LISTENER_HOST = '127.0.0.1'
LISTENER_PORT = find_free_port()
LISTENER_RESOURCE = '/listener'
SERVER_URL = f'http://{REST_API_HOST}:{REST_API_PORT}'