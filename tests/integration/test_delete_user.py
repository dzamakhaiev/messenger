import unittest
from tests.test_framework import TestFramework
from helpers.data import corrupt_json_field, remove_json_field
from helpers.network import find_free_port


class DeleteUserTest(TestFramework):

    def setUp(self):
        self.delete_json = {'user_id': '', 'session_id': ''}
        user = self.create_new_user()
        self.log_in_with_listener_url(user, find_free_port())
        self.delete_json['user_id'] = user.user_id
        self.delete_json['session_id'] = user.session_id

    def test_delete_user_positive(self):
        response = self.delete_user(self.delete_json)
        self.assertEqual(200, response.status_code, msg=response.text)
        self.assertEqual('User deleted.', response.text, msg=response.text)

    def test_validation_error(self):
        incorrect_json = remove_json_field(self.delete_json, 'session_id')
        response = self.delete_user(incorrect_json)
        self.assertEqual(401, response.status_code, msg=response.text)

    def test_incorrect_data(self):
        incorrect_json = corrupt_json_field(self.delete_json, 'session_id')
        response = self.delete_user(incorrect_json)
        self.assertEqual(401, response.status_code, msg=response.text)


if __name__ == '__main__':
    unittest.main()
