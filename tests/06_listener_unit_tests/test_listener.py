import os
from unittest import TestCase, skipIf, mock
from scripts.get_container_info import docker_is_running, container_is_running
from server_side.app import listener
from server_side.app import settings
from tests import test_data
from flask import Flask


app = Flask(__name__)


RUN_INSIDE_DOCKER = int(os.environ.get('RUN_INSIDE_DOCKER', 0))
CI_RUN = int(os.environ.get('CI_RUN', 0))
CONTAINER_NAME = 'rabbitmq-ci' if CI_RUN else 'rabbitmq'
DOCKER_RUNNING = docker_is_running()
CONTAINER_RUNNING = container_is_running(CONTAINER_NAME)
CONDITION = not (DOCKER_RUNNING and CONTAINER_RUNNING)
REASON = f'Docker/{CONTAINER_NAME} container is not running'

CONTAINER_NAME2 = 'postgres-ci' if CI_RUN else 'postgres'
DOCKER_RUNNING2 = docker_is_running()
CONTAINER_RUNNING2 = container_is_running(CONTAINER_NAME2)
CONDITION2 = not (DOCKER_RUNNING2 and CONTAINER_RUNNING2)
REASON2 = f'Docker/{CONTAINER_NAME2} container is not running'


class TestListener(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = listener.service
        cls.users = {}
        cls.user = None

    def create_user(self):
        user = listener.User(**test_data.USER_CREATE_JSON)
        user_id = self.service.create_user(user)
        self.users[user_id] = user
        self.user = user
        return user_id

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

    @skipIf(CONDITION, REASON)
    @skipIf(CONDITION2, REASON2)
    def test_create_token(self):
        # Preconditions and test data
        user_id = self.create_user()

        # Create token for created user
        token = listener.create_token(user_id=user_id, username=self.user.username)
        self.assertTrue(token)
        self.assertTrue(isinstance(token, str))

        # Check that token exists in databases
        token_db = self.service.get_user_token(user_id=user_id)
        self.assertEqual(token, token_db)

    @skipIf(CONDITION, REASON)
    @skipIf(CONDITION2, REASON2)
    def test_check_token(self):

        # Preconditions and test data
        user_id = self.create_user()
        token = listener.create_token(user_id=user_id, username=self.user.username)

        # Case 1: check_token returns None, None for valid token
        with app.test_request_context(headers={'Authorization': f'Bearer {token}'}):
            result_tuple = listener.check_token()
            self.assertEqual(result_tuple, (None, None))

        # Case 2: check no token
        with app.test_request_context(headers={'Authorization': ''}):
            error_tuple = listener.check_token()
            self.assertEqual(error_tuple, (settings.NOT_AUTHORIZED, 401))

        # Case 3: compare two different, but valid tokes
        with app.test_request_context(headers={'Authorization': f'Bearer {token}'}):
            with mock.patch('server_side.app.listener.settings.TOKEN_EXP_MINUTES', 666):
                self.service.delete_user_token(user_id=user_id)
                another_token = listener.create_token(user_id=user_id, username=self.user.username)
            error_tuple = listener.check_token()
            self.assertEqual(error_tuple, (settings.NOT_AUTHORIZED, 401))

        # Case 4: check expired token
        with mock.patch('server_side.app.listener.settings.TOKEN_EXP_MINUTES', -60*24):
            token = listener.create_token(user_id=user_id, username=self.user.username)
        with app.test_request_context(headers={'Authorization': f'Bearer {token}'}):
            error_tuple = listener.check_token()
            self.assertEqual(error_tuple, (settings.INVALID_TOKEN, 401))

        # Case 5: check invalid token
        with app.test_request_context(headers={'Authorization': 'Bearer invalid_token'}):
            error_tuple = listener.check_token()
            self.assertEqual(error_tuple, (settings.INVALID_TOKEN, 401))

    def tearDown(self):
        if self.users:
            for user_id in self.users:
                self.service.delete_user(user_id=user_id)

    @classmethod
    def tearDownClass(cls):
        # Drop all tables in HDD database
        query = "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
        # cls.service.hdd_db_handler.cursor_with_commit(query, [])
