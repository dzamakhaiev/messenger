import unittest
import test_data
from copy import copy
from time import sleep
from queue import Queue
from datetime import datetime

from tests.test_framework import TestFramework
from helpers.network import find_free_port
from helpers.data import corrupt_json_field, remove_json_field
from client_side.backend.listener import run_listener
from client_side.backend.settings import LISTENER_HOST


class MessagesTest(TestFramework):

    def setUp(self):
        self.new_user_id = None
        login_json = {'username': test_data.USERNAME, 'password': test_data.PASSWORD, 'user_address': 'some_ip'}
        response = self.log_in(login_json)

        self.session_id = response.json()['session_id']
        self.user_id = response.json()['user_id']
        self.username = test_data.USERNAME

        user_json = {'username': test_data.ANOTHER_USER, 'session_id': self.session_id}
        response = self.get_user_id(user_json)
        self.another_user_id = response.json()['user_id']

        self.correct_json = {'message': 'test', 'sender_id': self.user_id, 'sender_username': self.username,
                             'receiver_id': self.another_user_id, 'session_id': self.session_id,
                             'send_date': datetime.now().strftime(test_data.DATETIME_FORMAT)}

    def create_new_msg_json(self):
        self.msg_json = copy(self.correct_json)
        self.msg_json['receiver_id'] = self.new_user_id

    def log_in_as_another_user(self, listener_port):
        # Store listener address in DB during login operation
        url = f'http://{LISTENER_HOST}:{listener_port}'
        login_json = {'username': self.new_username, 'password': test_data.PASSWORD, 'user_address': url}
        response = self.log_in(login_json)

    def test_send_message_to_offline_user(self):
        response = self.send_message(self.correct_json)
        self.assertEqual(200, response.status_code, msg=response.text)

    def test_send_message(self):
        # Prepare message to send
        self.create_new_user()
        self.create_new_msg_json()

        # Start listener for another user and log in as another user
        port = find_free_port()
        self.run_client_listener(port)
        self.log_in_as_another_user(port)

        # Send message to another user
        response = self.send_message(self.msg_json)
        self.assertEqual(200, response.status_code, msg=response.text)
        self.assertEqual(self.new_queue.qsize(), 1, 'No message in queue.')

    def test_receive_msg_after_login(self):
        # Prepare message to send
        self.create_new_user()
        self.create_new_msg_json()

        # Send message to another user in offline
        response = self.send_message(self.msg_json)
        self.assertEqual(200, response.status_code, msg=response.text)

        # Start listener for another user and log in as another user
        port = find_free_port()
        self.run_client_listener(port)
        self.log_in_as_another_user(port)
        self.assertEqual(self.new_queue.qsize(), 1, 'No message in queue.')

    def test_validation_error(self):
        for field in ['message', 'sender_id', 'sender_username', 'receiver_id', 'session_id', 'send_date']:

            with self.subTest(f'Send message with no {field} field'):
                incorrect_json = remove_json_field(self.correct_json, field)
                response = self.send_message(incorrect_json)
                self.assertEqual(400, response.status_code, msg=response.text)

    def test_data_error(self):
        for field, code in [('sender_id', 400), ('sender_username', 401), ('receiver_id', 400), ('session_id', 401)]:

            with self.subTest(f'Send message with incorrect {field} field'):
                incorrect_json = corrupt_json_field(self.correct_json, field)
                response = self.send_message(incorrect_json)
                self.assertEqual(code, response.status_code, msg=response.text)


if __name__ == '__main__':
    unittest.main()
