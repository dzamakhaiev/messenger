import requests
from datetime import datetime
from helpers.network import get_local_ip
from client_side.backend import settings
from server_side.app.routes import LOGIN, USERS, MESSAGES
from server_side.app.settings import REST_API_PORT


SERVER_URL = f'http://localhost:{REST_API_PORT}'
LISTENER_URL = f'http://{get_local_ip()}:{settings.LISTENER_PORT}'
HEADERS = {'Content-type': 'application/json'}


class ClientSender:

    @staticmethod
    def post_request(url, json_dict=None):
        try:
            response = requests.post(url, json=json_dict, headers=HEADERS)
            return response
        except requests.exceptions.ConnectionError as e:
            print(e)

    @staticmethod
    def get_request(url, json_dict=None):
        try:
            response = requests.get(url, params=json_dict, headers=HEADERS)
            return response
        except requests.exceptions.ConnectionError as e:
            print(e)

    def login_request(self, json_dict, url=SERVER_URL + LOGIN, listener_url=LISTENER_URL):
        json_dict.update({'user_address': listener_url})
        response = self.post_request(url, json_dict)
        return response

    def message_request(self, json_dict, url=SERVER_URL + MESSAGES):
        json_dict['send_date'] = datetime.now().strftime(settings.DATETIME_FORMAT)
        response = self.post_request(url, json_dict)
        return response

    def user_request(self, json_dict, url=SERVER_URL + USERS):
        response = self.get_request(url, json_dict)
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

