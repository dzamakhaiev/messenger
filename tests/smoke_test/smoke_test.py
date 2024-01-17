import requests
from unittest import TestCase, main

LOCALHOST = 'http://127.0.0.1'
LOCAL_PORT = '5000'
REST_API_URL = f'{LOCALHOST}:{LOCAL_PORT}'

TASK_PORT = 5001
TASK_URL = f'{LOCALHOST}:{TASK_PORT}'


class SmokeTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.endpoints = ['/user', '/message']

    def test_get_method(self):
        for endpoint in self.endpoints:
            with self.subTest(f'Test GET method for endpoint: {endpoint}'):

                try:
                    response = requests.get(REST_API_URL + endpoint)
                    self.assertEqual(response.status_code, 200)
                except requests.exceptions.ConnectionError:
                    self.fail('No connection to the server')

    def test_put_method(self):
        for endpoint in self.endpoints:
            with self.subTest(f'Test PUT method for endpoint: {endpoint}'):

                try:
                    response = requests.put(REST_API_URL + endpoint)
                    self.assertEqual(response.status_code, 201)
                except requests.exceptions.ConnectionError:
                    self.fail('No connection to the server')

    def test_post_method(self):
        for endpoint in self.endpoints:
            with self.subTest(f'Test POST method for endpoint: {endpoint}'):

                try:
                    response = requests.post(REST_API_URL + endpoint)
                    self.assertEqual(response.status_code, 201)
                except requests.exceptions.ConnectionError:
                    self.fail('No connection to the server')

    def test_delete_method(self):
        for endpoint in self.endpoints:
            with self.subTest(f'Test DELETE method for endpoint: {endpoint}'):

                try:
                    response = requests.delete(REST_API_URL + endpoint)
                    self.assertEqual(response.status_code, 200)
                except requests.exceptions.ConnectionError:
                    self.fail('No connection to the server')

    def test_task_post_method(self):
        try:
            response = requests.post(TASK_URL + '/task')
            self.assertEqual(response.status_code, 201)
        except requests.exceptions.ConnectionError:
            self.fail('No connection to the server')

    def test_message_post_method(self):
        try:
            json_dict = {'message': 'test message', 'sender_id': 1, 'receiver_id': 2,
                         'sender_address': 'http://127.0.0.1:6666'}
            response = requests.post(REST_API_URL + '/message', json=json_dict)
            self.assertEqual(response.status_code, 201)
        except requests.exceptions.ConnectionError:
            self.fail('No connection to the server')


if __name__ == '__main__':
    main()
