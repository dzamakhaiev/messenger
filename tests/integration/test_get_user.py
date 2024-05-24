import unittest
from tests import test_data
from tests.test_framework import TestFramework
from helpers.data import corrupt_json_field, remove_json_field


class GetUserTest(TestFramework):

    def setUp(self):
        login_json = {'username': test_data.USERNAME, 'password': test_data.PASSWORD, 'user_address': 'some_ip'}
        response = self.log_in(login_json)
        self.session_id = response.json()['session_id']
        self.correct_json = {'username': test_data.USERNAME, 'session_id': self.session_id, 'request': 'get_user'}

    def test_get_user_id_positive(self):
        response = self.users_request(self.correct_json)
        self.assertEqual(200, response.status_code, msg=response.text)
        user_id = response.json()['user_id']
        self.assertEqual(test_data.USER_ID, user_id, f'Incorrect user_id: {user_id}')

    def test_validation_error(self):
        for field, code in (('session_id', 401), ('request', 400), ('username', 400)):
            with self.subTest(f'Get user with no "{field}" field.'):
                incorrect_json = remove_json_field(self.correct_json, field)
                response = self.users_request(incorrect_json)
                self.assertEqual(code, response.status_code, msg=response.text)

    def test_incorrect_data(self):
        for field, code in (('session_id', 401), ('request', 400), ('username', 404)):
            with self.subTest(f'Get user with incorrect "{field}" field.'):
                incorrect_json = corrupt_json_field(self.correct_json, field)
                response = self.users_request(incorrect_json)
                self.assertEqual(code, response.status_code, msg=response.text)


if __name__ == '__main__':
    unittest.main()
