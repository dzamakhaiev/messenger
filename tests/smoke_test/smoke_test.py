import requests
from unittest import TestCase, main

LOCALHOST = 'http://127.0.0.1'
LOCAL_PORT = '5000'
LOCAL_URL = f'{LOCALHOST}:{LOCAL_PORT}'


class SmokeTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.endpoints = ['/user', '/messages']

    def test_get_method(self):
        for endpoint in self.endpoints:
            with self.subTest(f'Test GET method for endpoint: {endpoint}'):

                try:
                    response = requests.get(LOCAL_URL + endpoint)
                    self.assertEqual(response.status_code, 200)
                except requests.exceptions.ConnectionError:
                    self.fail('No connection to the server')

    def test_put_method(self):
        for endpoint in self.endpoints:
            with self.subTest(f'Test PUT method for endpoint: {endpoint}'):

                try:
                    response = requests.put(LOCAL_URL + endpoint)
                    self.assertEqual(response.status_code, 201)
                except requests.exceptions.ConnectionError:
                    self.fail('No connection to the server')

    def test_post_method(self):
        for endpoint in self.endpoints:
            with self.subTest(f'Test POST method for endpoint: {endpoint}'):

                try:
                    response = requests.post(LOCAL_URL + endpoint)
                    self.assertEqual(response.status_code, 201)
                except requests.exceptions.ConnectionError:
                    self.fail('No connection to the server')

    def test_delete_method(self):
        for endpoint in self.endpoints:
            with self.subTest(f'Test DELETE method for endpoint: {endpoint}'):

                try:
                    response = requests.delete(LOCAL_URL + endpoint)
                    self.assertEqual(response.status_code, 200)
                except requests.exceptions.ConnectionError:
                    self.fail('No connection to the server')


if __name__ == '__main__':
    main()
