import socket
from random import randint


def find_free_port(port=5005):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('localhost', port)) == 0:
            return find_free_port(port=port + randint(0, 995))
        else:
            return port


LISTENER_HOST = '0.0.0.0'
LISTENER_PORT = find_free_port()
LISTENER_URL = f'http://{LISTENER_HOST}:{LISTENER_PORT}'
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FORMAT = "%(asctime)s %(levelname)s %(module)s: %(message)s"
