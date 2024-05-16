import unittest
from datetime import datetime
from threading import Thread
from tests.test_framework import TestFramework
from helpers.network import find_free_port
from tests import test_data


class LoadTest(TestFramework):

    def setUp(self):
        self.default_port = find_free_port()
        login_json = {'username': test_data.USERNAME, 'password': test_data.PASSWORD}
        self.log_in_with_listener_url(login_json, self.default_port)
        response = self.log_in(login_json)

        self.session_id = response.json()['session_id']
        self.user_id = response.json()['user_id']
        self.username = test_data.USERNAME

    def send_n_messages(self, msg_json: dict, responses: list, messages_to_send=100):
        for i in range(messages_to_send):
            msg_json['message'] = f'test_{i}'
            msg_json['send_date'] = datetime.now().strftime(test_data.DATETIME_FORMAT)
            response = self.send_message(msg_json, sleep_time=0)
            responses.append(response)

    def test_min_offline_load(self):
        # Prepare message json
        msg_json = {'message': 'test', 'sender_id': self.user_id, 'sender_username': self.username,
                    'receiver_id': test_data.ANOTHER_USER_ID, 'session_id': self.session_id,
                    'send_date': datetime.now().strftime(test_data.DATETIME_FORMAT)}
        responses = []
        messages_to_send = 100

        # Send N messages to offline user
        self.send_n_messages(msg_json, responses)
        self.assertEqual(len(responses), messages_to_send)

        for response in responses:
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.text, 'Message sent.')

    def test_min_load_one_user(self):
        # Create new user and start listener
        self.create_new_user()
        port = find_free_port()
        new_queue = self.run_client_listener(port)
        self.log_in_as_another_user(port)

        # Prepare message json
        msg_json = {'message': 'test', 'sender_id': self.user_id, 'sender_username': self.username,
                    'receiver_id': self.new_user_id, 'session_id': self.session_id}
        responses = []
        messages_to_send = 100

        # Send N messages to online user
        self.send_n_messages(msg_json, responses)
        self.assertEqual(len(responses), messages_to_send)
        self.assertEqual(len(responses), new_queue.qsize())

        for response in responses:
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.text, 'Message received.')


if __name__ == '__main__':
    unittest.main()
