import copy
import unittest
import requests
import test_data
from helpers.network import post_request


class LoginTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        url = test_data.SERVER_URL
        url += test_data.LOGIN
        cls.login_url = url

    def test_login_positive(self):
        correct_json = {'username': test_data.USERNAME, 'password': test_data.PASSWORD, 'user_address': 'some_ip'}
        response = post_request(self.login_url, correct_json)

        if isinstance(response, requests.ConnectionError):
            self.fail(response)

        else:
            self.assertEqual(200, response.status_code, msg=response.text)

            # Test response data
            user_id = response.json()['user_id']
            self.assertEqual(test_data.USER_ID, user_id, f'Incorrect user_id: {user_id}')
            session_id = response.json()['session_id']
            self.assertIsInstance(session_id, str, f'Unexpected session_id data type: {session_id}')

    def test_incorrect_login(self):
        correct_json = {'username': test_data.USERNAME, 'password': test_data.PASSWORD, 'user_address': 'some_ip'}

        for field in ('username', 'password', 'username and password'):

            with self.subTest(f'Login with incorrect {field}'):
                incorrect_json = copy.copy(correct_json)

                if field.count(' ') > 0:
                    incorrect_json['username'] = 'incorrect'
                    incorrect_json['password'] = 'incorrect'
                else:
                    incorrect_json[field] = 'incorrect'

                response = post_request(self.login_url, incorrect_json)
                if isinstance(response, requests.ConnectionError):
                    self.fail(response)
                else:
                    self.assertEqual(401, response.status_code, msg=response.text)
                    self.assertEqual('Incorrect username or password.', response.text)


if __name__ == '__main__':
    unittest.main()
