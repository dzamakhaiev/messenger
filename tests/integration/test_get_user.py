import unittest
from tests import test_data
from tests.test_framework import TestFramework
from helpers.data import corrupt_json_field, remove_json_field


class GetUserTest(TestFramework):

    def setUp(self):
        self.correct_json = {'username': test_data.USERNAME}

    def test_get_user_id_positive(self):
        response = self.get_user(self.correct_json)
        self.assertEqual(200, response.status_code, msg=response.text)
        user_id = response.json()['user_id']
        self.assertEqual(test_data.USER_ID, user_id, f'Incorrect user_id: {user_id}')

    def test_validation_error(self):
        incorrect_json = remove_json_field(self.correct_json, 'username')
        response = self.get_user(incorrect_json)
        self.assertEqual(400, response.status_code, msg=response.text)

    def test_incorrect_data(self):
        incorrect_json = corrupt_json_field(self.correct_json, 'username')
        response = self.get_user(incorrect_json)
        self.assertEqual(404, response.status_code, msg=response.text)


if __name__ == '__main__':
    unittest.main()
