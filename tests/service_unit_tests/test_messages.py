import socket
from unittest import TestCase, mock
from tests.database_mocks import get_hdd_db_handler, get_ram_db_handler, get_mq_handler
from server_side.app.service import Service
from server_side.app.models import User
from tests import test_data


LOCAL_IP = socket.gethostbyname(socket.gethostname())


class TestUser(TestCase):

    def setUp(self):
        self.service = Service(hdd_db_handler=get_hdd_db_handler(),
                               ram_db_handler=get_ram_db_handler(),
                               mq_handler=get_mq_handler())

        self.user = User(**test_data.USER_CREATE_JSON)

    def test_check_url(self):
        # First case: URL with local IP in host
        port = 5000
        url = f'https://{LOCAL_IP}:{port}'
        converted_url = self.service.check_url(url)
        self.assertIn('localhost', converted_url)

        # Second case: URL with localhost
        port = 5000
        url = f'https://{'127.0.0.1'}:{port}'
        converted_url = self.service.check_url(url)
        self.assertIn('localhost', converted_url)

        # Third case: URL without local IP in host
        port = 5000
        url = f'https://{'192.168.0.1'}:{port}'
        converted_url = self.service.check_url(url)
        self.assertNotIn('localhost', converted_url)

    @mock.patch('server_side.app.service.requests.post')
    def test_send_message(self, mock_post):
        mock_response = mock.Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        url = f'https://{'192.168.0.1'}:{5000}'
        msg_json = {'key': 'value'}

        response = self.service.send_message(url, msg_json=msg_json)
        mock_post.assert_called_once_with(url, json=msg_json, timeout=5)
        self.assertEqual(response.status_code, 201)
