import unittest
from server_side.app.listener import health_check


class HealthTest(unittest.TestCase):

    def test_health(self):
        response, status_code = health_check()
        self.assertEqual(response, 'OK')
        self.assertEqual(status_code, 200)


if __name__ == '__main__':
    unittest.main()
