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
        self.mock_response = mock.Mock()

    @staticmethod
    def create_message_from_db_like():
        return (test_data.MESSAGE_ID,
                test_data.USER_MESSAGE_JSON.get('sender_id'),
                test_data.USER_MESSAGE_JSON.get('receiver_id'),
                test_data.USER_MESSAGE_JSON.get('sender_username'),
                test_data.USER_MESSAGE_JSON.get('message'),
                test_data.USER_MESSAGE_JSON.get('send_date'))

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
        self.mock_response.status_code = 201
        mock_post.return_value = self.mock_response

        url = f'https://{'192.168.0.1'}:{5000}'
        msg_json = {'key': 'value'}

        response = self.service.send_message(url, msg_json=msg_json)
        mock_post.assert_called_once_with(url, json=msg_json, timeout=5)
        self.assertEqual(response.status_code, 201)

    def test_store_message_to_db(self):
        self.service.store_message_to_db(test_data.USER_MESSAGE_JSON)
        self.service.hdd_db_handler.insert_message.assert_called_once_with(
            test_data.USER_MESSAGE_JSON.get('sender_id'),
            test_data.USER_MESSAGE_JSON.get('receiver_id'),
            test_data.USER_MESSAGE_JSON.get('sender_username'),
            test_data.USER_MESSAGE_JSON.get('message'))

    def test_get_messages(self):
        # First case: database has messages
        message = self.create_message_from_db_like()
        self.service.hdd_db_handler.get_user_messages.return_value = [message]
        messages = self.service.get_messages(test_data.USER_ID)
        self.assertEqual(messages, [message])

        # Second case: database has no messages
        self.service.hdd_db_handler.get_user_messages.return_value = []
        messages = self.service.get_messages(test_data.USER_ID)
        self.assertEqual(messages, [])

        # Check that internal mocked methods were called once with expected args
        self.service.hdd_db_handler.get_user_messages.assert_any_call(test_data.USER_ID)
