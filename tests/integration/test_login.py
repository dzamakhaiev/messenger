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


if __name__ == '__main__':
    unittest.main()
