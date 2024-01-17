import requests
from client_side.backend import settings


class ClientSender:

    def __init__(self):
        self.listener_url = f'http://{settings.LISTENER_HOST}:{settings.LISTENER_PORT}:{settings.LISTENER_RESOURCE}'

    def send_request(self, resource, json_dict=None):
        try:
            response = requests.post(url=settings.SERVER_URL + resource, json=json_dict)
        except requests.exceptions.ConnectionError:
            pass
