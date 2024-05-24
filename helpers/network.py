import socket
import requests
from random import randint


def find_free_port(port=5005):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('localhost', port)) == 0:
            return find_free_port(port=port + randint(0, 995))
        else:
            return port


def post_request(url, json_dict=None):
    try:
        response = requests.post(url, json=json_dict)
        return response
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        return e


def get_local_ip():
    return socket.gethostbyname(socket.gethostname())
