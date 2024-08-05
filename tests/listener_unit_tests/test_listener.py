import os
import json
from unittest import TestCase, mock, skipIf
from scripts.get_container_info import docker_is_running, container_is_running
from server_side.database.sqlite_handler import RAMDatabaseHandler
from server_side.database.postgres_handler import PostgresHandler
from server_side.broker.mq_handler import RabbitMQHandler
from server_side.app.service import Service
from server_side.app.models import User
from server_side.app import settings
from tests import test_data


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
        hdd_db_handler = PostgresHandler()
        ram_db_handler = RAMDatabaseHandler()
        mq_handler = RabbitMQHandler()

        hdd_db_handler.create_all_tables()
        ram_db_handler.create_all_tables()
        mq_handler.create_exchange(settings.MQ_EXCHANGE_NAME)
        mq_handler.create_and_bind_queue(settings.MQ_MSG_QUEUE_NAME, settings.MQ_EXCHANGE_NAME)
        mq_handler.create_and_bind_queue(settings.MQ_LOGIN_QUEUE_NAME, settings.MQ_EXCHANGE_NAME)

        cls.service = Service(hdd_db_handler, ram_db_handler, mq_handler)
        cls.users = {}
        cls.user = None

    def create_user(self):
        user = User(**test_data.USER_CREATE_JSON)
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
        from server_side.app.listener import create_token
        user_id = self.create_user()

        # Create token for created user
        token = create_token(user_id=user_id, username=self.user.username)

    def tearDown(self):
        if self.users:
            for user_id in self.users:
                self.service.delete_user(user_id=user_id)
