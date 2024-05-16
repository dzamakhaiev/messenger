import unittest
from copy import copy
from datetime import datetime

from tests.test_framework import TestFramework
from helpers.network import find_free_port
from tests import test_data


class LoadTest(TestFramework):

    def setUp(self):
        self.listener_port = find_free_port()
        login_json = {'username': test_data.USERNAME, 'password': test_data.PASSWORD}
        self.log_in_with_listener_url(login_json, self.listener_port)
        response = self.log_in(login_json)

        self.session_id = response.json()['session_id']
        self.user_id = response.json()['user_id']
        self.username = test_data.USERNAME

    def test_min_offline_load(self):
        msg_json = {'message': 'test', 'sender_id': self.user_id, 'sender_username': self.username,
                    'receiver_id': test_data.ANOTHER_USER_ID, 'session_id': self.session_id}
        responses = []
        messages_to_send = 100

        # Send N messages to offline user
        for i in range(messages_to_send):
            msg_json['message'] = f'test_{i}'
            msg_json['send_date'] = datetime.now().strftime(test_data.DATETIME_FORMAT)
            response = self.send_message(msg_json, sleep_time=0)
            responses.append(response)

        self.assertEqual(len(responses), messages_to_send)
        for response in responses:
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.text, 'Message sent.')


if __name__ == '__main__':
    unittest.main()
