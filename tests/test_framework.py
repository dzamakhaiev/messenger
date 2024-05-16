import unittest
import requests
from time import sleep
from queue import Queue
from random import randint

from helpers.network import post_request
from client_side.backend.listener import run_listener
from client_side.backend.settings import LISTENER_HOST
from server_side.database.db_handler import HDDDatabaseHandler
from tests import settings


class TestFramework(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.login_url = settings.SERVER_URL + settings.LOGIN
        cls.users_url = settings.SERVER_URL + settings.USERS
        cls.messages_url = settings.SERVER_URL + settings.MESSAGES
        cls.db_handler = HDDDatabaseHandler()
        cls.new_user_id = None
        cls.new_username = 'new_user_{}'
        cls.new_session_id = None
        cls.new_phone_number = '11112222'

    def post_request(self, url, json_dict, sleep_time=0.1):
        response = post_request(url, json_dict)
        if isinstance(response, requests.ConnectionError):
            self.fail('Request failed.')
        sleep(sleep_time)
        return response

    def log_in(self, json_dict):
        response = self.post_request(url=self.login_url, json_dict=json_dict)
        return response

    def log_in_with_listener_url(self, login_json, listener_port):
        url = f'http://{LISTENER_HOST}:{listener_port}'
        login_json['user_address'] = url
        response = self.log_in(login_json)
        return response

    def get_user_id(self, json_dict):
        response = self.post_request(url=self.users_url, json_dict=json_dict)
        return response

    def send_message(self, json_dict, sleep_time=0.1):
        response = self.post_request(url=self.messages_url, json_dict=json_dict, sleep_time=sleep_time)
        return response

    def create_new_user(self):
        self.new_username = self.new_username.format(randint(0, 10**6))
        self.db_handler.insert_user(username=self.new_username, phone_number=self.new_phone_number)
        self.new_user_id = self.db_handler.get_user_id(self.new_username)

    def run_client_listener(self, port):
        queue = Queue()
        run_listener(queue, port=port)
        return queue

    def tearDown(self):
        if self.new_user_id:
            self.db_handler.delete_user(username=self.new_username)
