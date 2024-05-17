import unittest
from datetime import datetime
from threading import Thread
from tests.test_framework import TestFramework
from helpers.network import find_free_port
from tests import test_data


class LoadTest(TestFramework):

    def setUp(self):
        self.user = self.create_new_user()
        self.log_in_with_listener_url(user=self.user, listener_port=find_free_port())
        self.msg_json = {'message': 'test', 'sender_id': self.user.user_id, 'sender_username': self.user.username,
                         'receiver_id': test_data.ANOTHER_USER_ID, 'session_id': self.user.session_id,
                         'send_date': datetime.now().strftime(test_data.DATETIME_FORMAT)}

    def send_n_messages(self, msg_json: dict, responses: list, messages_to_send=100):
        for i in range(messages_to_send):
            msg_json['message'] = f'test_{i}'
            msg_json['send_date'] = datetime.now().strftime(test_data.DATETIME_FORMAT)
            response = self.send_message(msg_json, sleep_time=0)
            responses.append(response)

    def test_min_offline_load(self):
        # Prepare message json
        responses = []
        messages_to_send = 100

        # Send N messages to offline user
        self.send_n_messages(self.msg_json, responses, messages_to_send)
        self.assertEqual(len(responses), messages_to_send)

        for response in responses:
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.text, 'Message sent.')

    def test_min_load_one_user(self):
        # Create new user and prepare message to send
        new_user = self.create_new_user()
        msg_json = self.create_new_msg_json(receiver_id=new_user.user_id)

        # Start listener for new user and log in as new user
        port = find_free_port()
        new_queue = self.run_client_listener(port)
        self.log_in_with_listener_url(new_user, port)

        # Send N messages to online user
        responses = []
        messages_to_send = 100
        self.send_n_messages(msg_json, responses, messages_to_send)
        self.assertEqual(len(responses), messages_to_send)
        self.assertEqual(len(responses), new_queue.qsize())

        for response in responses:
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.text, 'Message received.')

    def test_min_load_two_users(self):
        # Start listener for default user
        default_queue = self.run_client_listener(self.user.listener_port)

        # Start listener for new user and log in as new user
        new_user = self.create_new_user()
        port = find_free_port()
        new_queue = self.run_client_listener(port)
        self.log_in_with_listener_url(new_user, port)

        # Prepare message json for both users
        msg_to_new_user = self.create_new_msg_json(receiver_id=new_user.user_id)
        msg_to_default_user = self.create_new_msg_json(sender_id=new_user.user_id, sender_username=new_user.username,
                                                       receiver_id=self.user.user_id, session_id=new_user.session_id)
        default_responses = []
        new_responses = []
        messages_to_send = 100

        # Send N messages to both online users
        thread_for_default_user = Thread(target=self.send_n_messages,
                                         args=(msg_to_new_user, default_responses, messages_to_send))
        thread_for_new_user = Thread(target=self.send_n_messages,
                                     args=(msg_to_default_user, new_responses, messages_to_send))

        # Start and wait both threads
        thread_for_default_user.start()
        thread_for_new_user.start()
        thread_for_default_user.join()
        thread_for_new_user.join()

        # Check both lists with responses
        self.assertEqual(len(default_responses), messages_to_send)
        self.assertEqual(len(new_responses), messages_to_send)
        self.assertEqual(len(default_responses), default_queue.qsize())
        self.assertEqual(len(new_responses), new_queue.qsize())

        for response in default_responses:
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.text, 'Message received.')

        for response in new_responses:
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.text, 'Message received.')


if __name__ == '__main__':
    unittest.main()
