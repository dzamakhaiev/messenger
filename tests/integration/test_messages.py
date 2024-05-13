import unittest
import requests
import test_data
from time import sleep
from queue import Queue
from datetime import datetime

from helpers.network import post_request
from helpers.data import corrupt_json_field, remove_json_field
from client_side.backend.listener import run_listener
from client_side.backend.settings import LISTENER_URL


class MessagesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        url = test_data.SERVER_URL
        cls.login_url = url + test_data.LOGIN
        cls.users_url = url + test_data.USERS
        cls.messages_url = url + test_data.MESSAGES

    def setUp(self):
        correct_json = {'username': test_data.USERNAME, 'password': test_data.PASSWORD, 'user_address': 'some_ip'}
        response = post_request(self.login_url, correct_json)

        self.session_id = response.json()['session_id']
        self.user_id = response.json()['user_id']
        self.username = test_data.USERNAME

        correct_json = {'username': test_data.ANOTHER_USER, 'session_id': self.session_id}
        response = post_request(self.users_url, correct_json)
        self.another_user_id = response.json()['user_id']

        self.correct_json = {'message': 'test', 'sender_id': self.user_id, 'sender_username': self.username,
                             'receiver_id': self.another_user_id, 'session_id': self.session_id,
                             'send_date': datetime.now().strftime(test_data.DATETIME_FORMAT)}

    def log_in_as_another_user(self, url=LISTENER_URL):
        # Store listener address in DB
        correct_json = {'username': test_data.ANOTHER_USER, 'password': test_data.PASSWORD, 'user_address': url}
        response = post_request(self.login_url, correct_json)
        pass

    def test_send_message_to_offline_user(self):
        response = post_request(self.messages_url, self.correct_json)

        if isinstance(response, requests.ConnectionError):
            self.fail(response)

        else:
            self.assertEqual(200, response.status_code, msg=response.text)

    def test_send_message(self):
        # Start listener for another user and log in as another user
        receiver_q = Queue()
        run_listener(receiver_q)
        self.log_in_as_another_user()

        # Send message to another user
        response = post_request(self.messages_url, self.correct_json)
        sleep(0.2)

        if isinstance(response, requests.ConnectionError):
            self.fail(response)

        else:
            self.assertEqual(200, response.status_code, msg=response.text)
            self.assertEqual(receiver_q.qsize(), 1)

    def test_validation_error(self):
        for field in ['message', 'sender_id', 'sender_username', 'receiver_id', 'session_id', 'send_date']:

            with self.subTest(f'Send message with no {field} field'):
                incorrect_json = remove_json_field(self.correct_json, field)
                response = post_request(self.messages_url, incorrect_json)

                if isinstance(response, requests.ConnectionError):
                    self.fail(response)

                else:
                    self.assertEqual(400, response.status_code, msg=response.text)

    def test_data_error(self):
        for field, code in [('sender_id', 400), ('sender_username', 401), ('receiver_id', 400), ('session_id', 401)]:

            with self.subTest(f'Send message with incorrect {field} field'):
                incorrect_json = corrupt_json_field(self.correct_json, field)
                response = post_request(self.messages_url, incorrect_json)

                if isinstance(response, requests.ConnectionError):
                    self.fail(response)

                else:
                    self.assertEqual(code, response.status_code, msg=response.text)


if __name__ == '__main__':
    unittest.main()
