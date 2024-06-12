import socket
import requests
from datetime import datetime
from client_side.backend import settings
from server_side.app.routes import LOGIN, USERS, MESSAGES
from server_side.app.settings import REST_API_PORT


SERVER_URL = f'http://192.168.50.100:{REST_API_PORT}'
LISTENER_URL = f'http://{socket.gethostbyname(socket.gethostname())}:{settings.LISTENER_PORT}'
HEADERS = {'Content-type': 'application/json', 'Authorization': ''}


class ClientSender:

    @staticmethod
    def post_request(url, json_dict=None, headers=None):
        try:
            if headers is None:
                headers = HEADERS

            response = requests.post(url, json=json_dict, headers=headers)
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
        response = self.post_request(url, json_dict, )
        return response

    def message_request(self, json_dict, token, url=SERVER_URL + MESSAGES):
        HEADERS['Authorization'] = f'Bearer {token}'
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
    token = sender_json.get('token')

    response = client.user_request('user_2')
    receiver_json = response.json()
    receiver_id = receiver_json.get('user_id')

    msg_json = {'message': 'Pidor!', 'sender_id': 1, 'receiver_id': 2, 'sender_address': '127.0.0.1:666'}
    response = client.message_request(json_dict=msg_json, token=token)

