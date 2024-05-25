import unittest
from tests import test_data
from datetime import datetime

from tests.test_framework import TestFramework
from helpers.network import find_free_port
from helpers.data import corrupt_json_field, remove_json_field


class MessagesTest(TestFramework):

    def setUp(self):
        self.user = self.create_new_user()
        self.log_in_with_listener_url(user=self.user, listener_port=find_free_port())
        self.msg_json = {'message': 'test', 'sender_id': self.user.user_id, 'sender_username': self.user.username,
                         'receiver_id': test_data.ANOTHER_USER_ID, 'session_id': self.user.session_id,
                         'send_date': datetime.now().strftime(test_data.DATETIME_FORMAT)}

    def test_send_message_to_offline_user(self):
        new_user = self.create_new_user()
        msg_json = self.create_new_msg_json(receiver_id=new_user.user_id)
        response = self.send_message(msg_json)
        self.assertEqual(200, response.status_code, msg=response.text)
        self.assertEqual(response.text, 'Message processed.')

    def test_send_message(self):
        # Create new user and prepare message to send
        new_user = self.create_new_user()
        msg_json = self.create_new_msg_json(receiver_id=new_user.user_id)

        # Start listener for new user and log in as new user
        port = find_free_port()
        new_queue = self.run_client_listener(port)
        self.log_in_with_listener_url(new_user, port)

        # Send message to another user
        response = self.send_message(msg_json)
        self.assertEqual(200, response.status_code, msg=response.text)
        self.assertEqual(response.text, 'Message processed.')
        self.assertEqual(new_queue.qsize(), 1, 'No message in queue.')

    def test_send_mutual_messages(self):
        # Run listener for default user
        default_queue = self.run_client_listener(self.user.listener_port)

        # Create new user
        new_user = self.create_new_user()
        new_port = find_free_port()
        new_queue = self.run_client_listener(new_port)
        self.log_in_with_listener_url(user=new_user, listener_port=new_port)

        # Create message json for both users
        msg_to_new_user = self.create_new_msg_json(receiver_id=new_user.user_id)
        msg_to_default_user = self.create_new_msg_json(sender_id=new_user.user_id, sender_username=new_user.username,
                                                       receiver_id=self.user.user_id, session_id=new_user.session_id)

        # Send messages to both users
        response_new = self.send_message(msg_to_new_user)
        response_default = self.send_message(msg_to_default_user)

        # Check response and listener queue
        self.assertEqual(200, response_new.status_code, msg=response_new.text)
        self.assertEqual(200, response_default.status_code, msg=response_default.text)
        self.assertEqual(new_queue.qsize(), 1, 'No message in queue.')
        self.assertEqual(default_queue.qsize(), 1, 'No message in queue.')

    def test_receive_msg_after_login(self):
        # Create new user and prepare message to send
        another_user = self.create_new_user()
        msg_json = self.create_new_msg_json(receiver_id=another_user.user_id)

        # Send message to another user in offline
        response = self.send_message(msg_json)
        self.assertEqual(200, response.status_code, msg=response.text)
        self.assertEqual(response.text, 'Message processed.')

        # Start listener for another user and log in as another user
        port = find_free_port()
        new_queue = self.run_client_listener(port)
        self.log_in_with_listener_url(another_user, port)
        self.assertEqual(new_queue.qsize(), 1, 'No message in queue.')

    def test_validation_error(self):
        for field in ['message', 'sender_id', 'sender_username', 'receiver_id', 'session_id', 'send_date']:

            with self.subTest(f'Send message with no "{field}" field.'):
                incorrect_json = remove_json_field(self.msg_json, field)
                response = self.send_message(incorrect_json)
                self.assertEqual(400, response.status_code, msg=response.text)

    def test_data_error(self):
        for field, code in [('sender_id', 400), ('sender_username', 401), ('receiver_id', 400), ('session_id', 401)]:

            with self.subTest(f'Send message with incorrect "{field}" field.'):
                incorrect_json = corrupt_json_field(self.msg_json, field)
                response = self.send_message(incorrect_json)
                self.assertEqual(code, response.status_code, msg=response.text)


if __name__ == '__main__':
    unittest.main()
