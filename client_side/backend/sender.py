import requests
from client_side.backend import settings
from server_side.app.routes import LOGIN, USERS, MESSAGES
from server_side.app.settings import REST_API_HOST, REST_API_PORT


SERVER_URL = f'http://{REST_API_HOST}:{REST_API_PORT}'


class ClientSender:

    def __init__(self):
        self.listener_url = f'http://{settings.LISTENER_HOST}:{settings.LISTENER_PORT}:{settings.LISTENER_RESOURCE}'

    @staticmethod
    def post_request(url, json_dict=None):
        try:
            response = requests.post(url, json=json_dict)
            return response
        except requests.exceptions.ConnectionError:
            pass

    @staticmethod
    def get_request(url):
        try:
            response = requests.get(url)
            return response
        except requests.exceptions.ConnectionError:
            pass

    def login_request(self, json_dict, url=SERVER_URL + LOGIN):
        response = self.post_request(url, json_dict)
        return response

    def message_request(self, json_dict, url=SERVER_URL + MESSAGES):
        response = self.post_request(url, json_dict)
        return response

    def user_request(self, username, url=SERVER_URL + USERS):
        url += username
        response = self.get_request(url)
        return response


if __name__ == '__main__':
    client = ClientSender()
    response = client.login_request(json_dict={'username': 'user_1', 'password': 'qwerty'})
    sender_json = response.json()
    session_id = sender_json.get('session_id')

    response = client.user_request('user_2')
    receiver_json = response.json()
    receiver_id = receiver_json.get('user_id')

    msg_json = {'message': 'Pidor!', 'sender_id': 1, 'receiver_id': 2,
                'session_id': session_id, 'sender_address': '127.0.0.1:666'}
    response = client.message_request(json_dict=msg_json)

