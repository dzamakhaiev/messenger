import requests
from client_side.backend import settings


class ClientSender:

    def __init__(self):
        self.listener_url = f'http://{settings.LISTENER_HOST}:{settings.LISTENER_PORT}:{settings.LISTENER_RESOURCE}'

    @staticmethod
    def send_request(resource, json_dict=None):
        try:
            response = requests.post(url=settings.SERVER_URL + resource, json=json_dict)
            return response
        except requests.exceptions.ConnectionError:
            pass

    @staticmethod
    def user_id_request(username, resource='/users/'):
        try:
            response = requests.get(url=settings.SERVER_URL + resource + username)
            return response
        except requests.exceptions.ConnectionError:
            pass


if __name__ == '__main__':
    client = ClientSender()
    response = client.send_request('/login/', {'username': 'user_1', 'password': 'qwerty'})
    sender_json = response.json()

    response = client.user_id_request('user_2')
    receiver_json = response.json()

