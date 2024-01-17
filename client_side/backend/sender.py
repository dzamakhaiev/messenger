import requests
from client_side.backend import settings


class ClientSender:

    def __init__(self):
        self.listener_url = f'http://{settings.LISTENER_HOST}:{settings.LISTENER_PORT}'

    def send_request(self, json_dict=None):
        try:
            response = requests.post(url=settings.SERVER_URL, json=json_dict)
        except requests.exceptions.ConnectionError:
            pass
