import json
from unittest import TestCase, mock
from pika.channel import Channel
from pika.spec import Basic, BasicProperties
from server_side.app.sender import process_message, process_login
from server_side.app import settings
from tests import test_data


class TestSender(TestCase):

    def setUp(self):
        self.mock_response = mock.Mock()

    @staticmethod
    def create_message_json():
        return {'sender_id': test_data.USER_MESSAGE_JSON.get('sender_id'),
                'receiver_id': test_data.USER_MESSAGE_JSON.get('receiver_id'),
                'sender_username': test_data.USER_MESSAGE_JSON.get('sender_username'),
                'message': test_data.USER_MESSAGE_JSON.get('message'),
                'send_date': test_data.USER_MESSAGE_JSON.get('send_date')}

    @staticmethod
    def create_message_from_db_like():
        return (test_data.MESSAGE_ID,
                test_data.USER_MESSAGE_JSON.get('sender_id'),
                test_data.USER_MESSAGE_JSON.get('receiver_id'),
                test_data.USER_MESSAGE_JSON.get('sender_username'),
                test_data.USER_MESSAGE_JSON.get('message'),
                test_data.USER_MESSAGE_JSON.get('send_date'))

    def test_process_message(self):

        # Mock RabbitMQ objects
        channel = mock.Mock(spec=Channel)
        method = mock.Mock(spec=Basic.Deliver)
        properties = mock.Mock(spec=BasicProperties)
        method.delivery_tag = ''

        # Prepare queue message
        message_dict = self.create_message_json()
        message_dict['send_date'] = message_dict['send_date'].strftime(settings.DATETIME_FORMAT)
        queue_dict = {'address_list': [test_data.USER_ADDRESS], 'msg_json': message_dict}
        queue_json = json.dumps(queue_dict)
        body = queue_json.encode()

        # First case: correct data from RabbitMQ
        try:
            process_message(channel=channel, method=method, properties=properties, body=body)
        except (ValueError, AttributeError) as e:
            self.fail(e)

        # Second case: incorrect data type for decoding from bytes to string
        try:
            process_message(channel=channel, method=method, properties=properties, body=queue_dict)
            self.fail('')
        except AttributeError as e:
            self.assertTrue(isinstance(e, (BaseException,)))

        # Third case: incorrect data for json loader
        try:
            body = b'some incorrect data for json loader'
            process_message(channel=channel, method=method, properties=properties, body=body)
            self.fail('')
        except ValueError as e:
            self.assertTrue(isinstance(e, (BaseException,)))

    @mock.patch('server_side.app.service.Service.get_messages')
    def test_process_login(self, mock_get_messages):

        # Mock RabbitMQ objects
        channel = mock.Mock(spec=Channel)
        method = mock.Mock(spec=Basic.Deliver)
        properties = mock.Mock(spec=BasicProperties)
        method.delivery_tag = ''

        # Mocking HDD DB response
        expected_messages = [self.create_message_from_db_like()]
        mock_get_messages.return_value = expected_messages

        # Prepare queue login message
        queue_dict = {'user_id': test_data.USER_ID, 'user_address': test_data.USER_ADDRESS}
        queue_json = json.dumps(queue_dict)
        body = queue_json.encode()

        # First case: correct data from RabbitMQ
        try:
            process_login(channel=channel, method=method, properties=properties, body=body)
            mock_get_messages.assert_called_once_with(test_data.USER_ID)
        except (ValueError, AttributeError) as e:
            self.fail(e)

        # Second case: incorrect data type for decoding from bytes to string
        try:
            process_login(channel=channel, method=method, properties=properties, body=queue_dict)
            self.fail('')
        except AttributeError as e:
            self.assertTrue(isinstance(e, (BaseException,)))

        # Third case: incorrect data for json loader
        try:
            body = b'some incorrect data for json loader'
            process_login(channel=channel, method=method, properties=properties, body=body)
            self.fail('')
        except ValueError as e:
            self.assertTrue(isinstance(e, (BaseException,)))