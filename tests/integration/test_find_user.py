import unittest
import requests
import test_data
from helpers.network import post_request


class UsersTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        url = test_data.SERVER_URL
        cls.login_url = url + test_data.LOGIN
        cls.users_url = url + test_data.USERS

    def setUp(self):
        correct_json = {'username': test_data.USERNAME, 'password': test_data.PASSWORD, 'user_address': 'some_ip'}
        response = post_request(self.login_url, correct_json)
        self.session_id = response.json()['session_id']

    def test_get_user_id_positive(self):
        correct_json = {'username': test_data.USERNAME, 'session_id': self.session_id}
        response = post_request(self.users_url, correct_json)

        if isinstance(response, requests.ConnectionError):
            self.fail(response)

        else:
            self.assertEqual(200, response.status_code, msg=response.text)
            user_id = response.json()['user_id']
            self.assertEqual(test_data.USER_ID, user_id, f'Incorrect user_id: {user_id}')

    def test_get_no_user(self):
        incorrect_json = {'username': 'some user', 'session_id': self.session_id}
        response = post_request(self.users_url, incorrect_json)

        if isinstance(response, requests.ConnectionError):
            self.fail(response)
        else:
            self.assertEqual(404, response.status_code, msg=response.text)

    def test_get_user_id_negative(self):
        incorrect_json = {'session_id': self.session_id}
        response = post_request(self.users_url, incorrect_json)

        if isinstance(response, requests.ConnectionError):
            self.fail(response)
        else:
            self.assertEqual(400, response.status_code, msg=response.text)


if __name__ == '__main__':
    unittest.main()
