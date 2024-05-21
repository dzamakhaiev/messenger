import unittest
from tests import test_data
from tests.test_framework import TestFramework
from helpers.data import corrupt_json_field, remove_json_field
from helpers.data import create_username, create_phone_number, create_password


class UsersTest(TestFramework):

    def setUp(self):
        self.correct_json = {'username': create_username(), 'phone_number': create_phone_number(),
                             'password': create_password(), 'request': 'create_user'}

    def test_create_user_positive(self):
        response = self.users_request(self.correct_json)
        self.assertEqual(201, response.status_code, msg=response.text)
        user_id = response.json()['user_id']
        self.assertTrue(user_id, f'Incorrect user_id: {user_id}')

    def test_validation_error(self):
        for field, code in (('request', 400), ('username', 400)):
            with self.subTest(f'Create user with no "{field}" field.'):
                incorrect_json = remove_json_field(self.correct_json, field)
                response = self.users_request(incorrect_json)
                self.assertEqual(code, response.status_code, msg=response.text)

    def test_incorrect_data(self):
        for field, value in (('request', 'some'), ('username', None)):
            with self.subTest(f'Create user with incorrect value of "{field}" field.'):
                incorrect_json = corrupt_json_field(self.correct_json, field, value)
                response = self.users_request(incorrect_json)
                self.assertEqual(400, response.status_code, msg=response.text)


if __name__ == '__main__':
    unittest.main()
