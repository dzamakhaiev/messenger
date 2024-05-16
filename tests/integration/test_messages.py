import unittest
from tests import test_data
from copy import copy
from datetime import datetime

from tests.test_framework import TestFramework
from helpers.network import find_free_port
from helpers.data import corrupt_json_field, remove_json_field


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

    def create_new_msg_json(self, sender_id=None, username=None, receiver_id=None, session_id=None):
        self.msg_json = copy(self.correct_json)
        self.msg_json['sender_id'] = sender_id if sender_id else self.user_id
        self.msg_json['sender_username'] = username if username else self.username
        self.msg_json['receiver_id'] = receiver_id if receiver_id else self.new_user_id
        self.msg_json['session_id'] = session_id if session_id else self.session_id
        return copy(self.msg_json)

    def test_send_message_to_offline_user(self):
        response = self.send_message(self.correct_json)
        self.assertEqual(200, response.status_code, msg=response.text)
        self.assertEqual(response.text, 'Message sent.')

    def test_send_message(self):
        # Create new user and prepare message to send
        self.create_new_user()
        self.create_new_msg_json()

        # Start listener for another user and log in as another user
        port = find_free_port()
        new_queue = self.run_client_listener(port)
        self.log_in_as_another_user(port)

        # Send message to another user
        response = self.send_message(self.msg_json)
        self.assertEqual(200, response.status_code, msg=response.text)
        self.assertEqual(response.text, 'Message received.')
        self.assertEqual(new_queue.qsize(), 1, 'No message in queue.')

    def test_send_mutual_messages(self):
        # Run listener for default user
        default_port = find_free_port()
        default_queue = self.run_client_listener(default_port)
        login_json = {'username': self.username, 'password': test_data.PASSWORD}
        self.log_in_with_listener_url(login_json, default_port)

        # Create new user
        self.create_new_user()
        new_port = find_free_port()
        new_queue = self.run_client_listener(new_port)
        self.log_in_as_another_user(new_port)

        # Create message json for first user to send to new user and to default user
        msg_to_new_user = self.create_new_msg_json()
        msg_to_default_user = self.create_new_msg_json(sender_id=self.new_user_id, username=self.new_username,
                                                       receiver_id=self.user_id, session_id=self.new_session_id)

        # Send messages to both users
        response_new = self.send_message(msg_to_new_user)
        response_default = self.send_message(msg_to_default_user)

        # Check response and listener queue
        self.assertEqual(200, response_new.status_code, msg=response_new.text)
        self.assertEqual(200, response_default.status_code, msg=response_default.text)
        self.assertEqual(new_queue.qsize(), 1, 'No message in queue.')
        self.assertEqual(default_queue.qsize(), 1, 'No message in queue.')

    def test_receive_msg_after_login(self):
        # Create new user and prepare message to send
        self.create_new_user()
        self.create_new_msg_json()

        # Send message to another user in offline
        response = self.send_message(self.msg_json)
        self.assertEqual(200, response.status_code, msg=response.text)
        self.assertEqual(response.text, 'Message sent.')

        # Start listener for another user and log in as another user
        port = find_free_port()
        new_queue = self.run_client_listener(port)
        self.log_in_as_another_user(port)
        self.assertEqual(new_queue.qsize(), 1, 'No message in queue.')

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
