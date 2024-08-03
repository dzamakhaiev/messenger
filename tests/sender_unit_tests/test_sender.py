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
