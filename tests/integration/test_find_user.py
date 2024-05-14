import unittest
import test_data
from tests.test_framework import TestFramework


class UsersTest(TestFramework):

    def setUp(self):
        login_json = {'username': test_data.USERNAME, 'password': test_data.PASSWORD, 'user_address': 'some_ip'}
        response = self.log_in(json_login)
        self.session_id = response.json()['session_id']
        self.correct_json = {'username': test_data.USERNAME, 'session_id': self.session_id}

    def test_get_user_id_positive(self):
        response = self.get_user_id(self.correct_json)
        self.assertEqual(200, response.status_code, msg=response.text)
        user_id = response.json()['user_id']
        self.assertEqual(test_data.USER_ID, user_id, f'Incorrect user_id: {user_id}')

    def test_get_no_user(self):
        incorrect_json = {'username': 'some user', 'session_id': self.session_id}
        response = self.get_user_id(incorrect_json)
        self.assertEqual(404, response.status_code, msg=response.text)

    def test_validation_error(self):
        incorrect_json = {'session_id': self.session_id}
        response = self.get_user_id(incorrect_json)
        self.assertEqual(400, response.status_code, msg=response.text)


if __name__ == '__main__':
    unittest.main()
