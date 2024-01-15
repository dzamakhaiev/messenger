import requests
from unittest import TestCase, main

LOCALHOST = 'http://127.0.0.1'
LOCAL_PORT = '5000'
LOCAL_URL = f'{LOCALHOST}:{LOCAL_PORT}'


class SmokeTest(TestCase):

    def test_get_method(self):
        try:
            response = requests.get(LOCAL_URL)
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.fail('No connection to the server')

    def test_put_method(self):
        try:
            response = requests.put(LOCAL_URL)
            self.assertEqual(response.status_code, 201)
        except requests.exceptions.ConnectionError:
            self.fail('No connection to the server')

    def test_post_method(self):
        try:
            response = requests.post(LOCAL_URL)
            self.assertEqual(response.status_code, 201)
        except requests.exceptions.ConnectionError:
            self.fail('No connection to the server')

    def test_delete_method(self):
        try:
            response = requests.delete(LOCAL_URL)
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.fail('No connection to the server')


if __name__ == '__main__':
    main()
