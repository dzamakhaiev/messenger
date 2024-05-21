import unittest
import requests
from copy import copy
from time import sleep
from queue import Queue
from random import randint
from datetime import datetime

from helpers.network import post_request
from client_side.backend.listener import run_listener
from client_side.backend.settings import LISTENER_HOST
from server_side.database.db_handler import HDDDatabaseHandler
from tests import test_data
from tests import settings


class User:

    def __init__(self, user_id, username, phone_number, password=test_data.PASSWORD):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.phone_number = phone_number
        self.session_id = None
        self.user_address = None
        self.listener_port = None


class TestFramework(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.login_url = settings.SERVER_URL + settings.LOGIN
        cls.users_url = settings.SERVER_URL + settings.USERS
        cls.messages_url = settings.SERVER_URL + settings.MESSAGES
        cls.db_handler = HDDDatabaseHandler()
        cls.users = []
        cls.msg_json = {}

    def post_request(self, url, json_dict, sleep_time=0.1):
        response = post_request(url, json_dict)
        if isinstance(response, requests.ConnectionError):
            self.fail(f'Request failed: {response}')
        sleep(sleep_time)
        return response

    def log_in(self, json_dict):
        response = self.post_request(url=self.login_url, json_dict=json_dict)
        return response

    def get_user_id(self, json_dict):
        response = self.post_request(url=self.users_url, json_dict=json_dict)
        return response

    def send_message(self, json_dict, sleep_time=0.1):
        response = self.post_request(url=self.messages_url, json_dict=json_dict, sleep_time=sleep_time)
        return response

    def log_in_with_listener_url(self, user: User, listener_port):
        user.user_address = f'http://{LISTENER_HOST}:{listener_port}'
        user.listener_port = listener_port
        login_json = {'username': user.username, 'password': user.password, 'user_address': user.user_address}
        response = self.log_in(login_json)

        if response.status_code == 200:
            user.session_id = response.json()['session_id']
        else:
            self.fail(response.text)
        return response

    def create_new_user(self):
        username = 'user_{}'.format(randint(1, 666))
        phone_number = '{}'.format(randint(10 ** 9, 10 ** 10 - 1))
        self.db_handler.insert_user(username=username, phone_number=phone_number)
        user_id = self.db_handler.get_user_id(username)

        user = User(user_id=user_id, username=username, phone_number=phone_number)
        self.users.append(user)
        return user

    def create_new_msg_json(self, **kwargs):
        msg_json = copy(self.msg_json)
        msg_json['sender_id'] = kwargs.get('sender_id', msg_json['sender_id'])
        msg_json['sender_username'] = kwargs.get('sender_username', msg_json['sender_username'])
        msg_json['receiver_id'] = kwargs.get('receiver_id', msg_json['receiver_id'])
        msg_json['session_id'] = kwargs.get('session_id', msg_json['session_id'])
        msg_json['message'] = kwargs.get('message', msg_json['message'])
        msg_json['send_date'] = datetime.now().strftime(test_data.DATETIME_FORMAT)
        return msg_json

    def run_client_listener(self, port):
        queue = Queue()
        run_listener(queue, port=port)
        return queue

    def tearDown(self):
        if self.users:
            for user in self.users:
                self.db_handler.delete_user(username=user.username)
