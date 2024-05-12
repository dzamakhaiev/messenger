import unittest
import requests
import test_data
from datetime import datetime
from helpers.network import post_request
from helpers.data import corrupt_json_field, remove_json_field


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

    def test_send_message_to_offline_user(self):
        response = post_request(self.messages_url, self.correct_json)

        if isinstance(response, requests.ConnectionError):
            self.fail(response)

        else:
            self.assertEqual(200, response.status_code, msg=response.text)

    def test_validation_error(self):
        for field in ['message', 'sender_id', 'sender_username', 'receiver_id', 'session_id', 'send_date']:

            with self.subTest(f'Send message with no {field} field'):
                incorrect_json = remove_json_field(self.correct_json, field)
                response = post_request(self.messages_url, incorrect_json)

                if isinstance(response, requests.ConnectionError):
                    self.fail(response)

                else:
                    self.assertEqual(400, response.status_code, msg=response.text)


if __name__ == '__main__':
    unittest.main()
