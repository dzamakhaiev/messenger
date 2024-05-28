import unittest
from tests.test_framework import TestFramework
from helpers.data import corrupt_json_field, remove_json_field
from helpers.network import find_free_port


class DeleteUserTest(TestFramework):

    def setUp(self):
        self.delete_json = {'user_id': '', 'session_id': '', 'request': 'delete_user'}
        user = self.create_new_user()
        self.log_in_with_listener_url(user, find_free_port())
        self.delete_json['user_id'] = user.user_id
        self.delete_json['session_id'] = user.session_id

    def test_delete_user_positive(self):
        response = self.users_request(self.delete_json)
        self.assertEqual(200, response.status_code, msg=response.text)
        self.assertEqual('User deleted.', response.text, msg=response.text)

    def test_validation_error(self):
        for field, code in (('user_id', 400), ('session_id', 401), ('request', 400)):
            with self.subTest(f'Create user with no "{field}" field.'):
                incorrect_json = remove_json_field(self.delete_json, field)
                response = self.users_request(incorrect_json)
                self.assertEqual(code, response.status_code, msg=response.text)

    def test_incorrect_data(self):
        for field, code in (('request', 400), ('session_id', 401)):
            with self.subTest(f'Create user with incorrect value of "{field}" field.'):
                incorrect_json = corrupt_json_field(self.delete_json, field)
                response = self.users_request(incorrect_json)
                self.assertEqual(code, response.status_code, msg=response.text)


if __name__ == '__main__':
    unittest.main()
