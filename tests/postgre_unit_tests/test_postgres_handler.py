import os
from datetime import datetime
from unittest import TestCase, skipIf
from docker import from_env
from docker.errors import DockerException
from server_side.database.postgres_handler import PostgresHandler
from logger.logger import Logger
from tests import test_data


postgres_test_logger = Logger('postgres_test_logger')


try:
    # Check docker is running
    docker = from_env()
    docker_running = True
    postgres_running = False

    # Check Postgres container is running
    containers = docker.containers.list()
    containers = [container.name for container in containers]
    if 'postgres' in containers or 'postgres-ci' in containers:
        postgres_running = True

except DockerException as e:
    docker_running = False
    postgres_running = False


RUN_INSIDE_DOCKER = int(os.environ.get('RUN_INSIDE_DOCKER', 0))
CI_RUN = int(os.environ.get('CI_RUN', 0))
CONDITION = not (docker_running and postgres_running)
REASON = 'Docker/postgres container is not running'
WAIT_MESSAGE_TIME = 0.3

postgres_test_logger.info(f'Postgres unit tests.\n'
                          f'Run inside docker: {RUN_INSIDE_DOCKER}\n'
                          f'Continuous Integration: {CI_RUN}\n'
                          f'Condition for skip tests: {CONDITION}')


class TestPostgres(TestCase):

    @classmethod
    def setUpClass(cls):

        if RUN_INSIDE_DOCKER and CI_RUN:
            client = docker.from_env()
            container = client.containers.get('postgres-ci')
            container_info = container.attrs

            networks = container_info.get('NetworkSettings').get('Networks')
            bridge_network = networks.get('bridge')
            ip_address = bridge_network.get('IPAddress')
            cls.postgres_host = ip_address

        else:
            cls.postgres_host = 'localhost'

        postgres_test_logger.info(f'Container Postgres runs on IP {cls.postgres_host}')

    def setUp(self):
        self.hdd_db_handler = PostgresHandler(host=self.postgres_host)

    @skipIf(CONDITION, REASON)
    def test_create_users_table(self):
        self.hdd_db_handler.create_users_table()

        query = 'SELECT EXISTS(SELECT relname FROM pg_class WHERE relname = %s)'
        result = self.hdd_db_handler.cursor_execute(query, ('users',))
        result = result.fetchone()
        self.assertTrue(result[0])

    @skipIf(CONDITION, REASON)
    def test_create_messages_table(self):
        self.hdd_db_handler.create_messages_table()

        query = 'SELECT EXISTS(SELECT relname FROM pg_class WHERE relname = %s)'
        result = self.hdd_db_handler.cursor_execute(query, ('messages',))
        result = result.fetchone()
        self.assertTrue(result[0])

    @skipIf(CONDITION, REASON)
    def test_create_address_table(self):
        self.hdd_db_handler.create_address_table()

        query = 'SELECT EXISTS(SELECT relname FROM pg_class WHERE relname = %s)'
        result = self.hdd_db_handler.cursor_execute(query, ('address',))
        result = result.fetchone()
        self.assertTrue(result[0])

    @skipIf(CONDITION, REASON)
    def test_create_user_address_table(self):
        self.hdd_db_handler.create_user_address_table()

        query = 'SELECT EXISTS(SELECT relname FROM pg_class WHERE relname = %s)'
        result = self.hdd_db_handler.cursor_execute(query, ('user_address',))
        result = result.fetchone()
        self.assertTrue(result[0])

    @skipIf(CONDITION, REASON)
    def test_create_tokens_table(self):
        self.hdd_db_handler.create_tokens_table()

        query = 'SELECT EXISTS(SELECT relname FROM pg_class WHERE relname = %s)'
        result = self.hdd_db_handler.cursor_execute(query, ('tokens',))
        result = result.fetchone()
        self.assertTrue(result[0])

    @skipIf(CONDITION, REASON)
    def test_create_public_keys_table(self):
        self.hdd_db_handler.create_public_keys_table()

        query = 'SELECT EXISTS(SELECT relname FROM pg_class WHERE relname = %s)'
        result = self.hdd_db_handler.cursor_execute(query, ('public_keys',))
        result = result.fetchone()
        self.assertTrue(result[0])

    @skipIf(CONDITION, REASON)
    def test_create_all_tables(self):
        self.hdd_db_handler.create_all_tables()
        all_tables = ['users', 'messages', 'address', 'user_address', 'tokens', 'public_keys']

        for table in all_tables:
            with self.subTest(f'Test "{table}" table exists.'):

                query = 'SELECT EXISTS(SELECT relname FROM pg_class WHERE relname = %s)'
                result = self.hdd_db_handler.cursor_execute(query, (table,))
                result = result.fetchone()
                self.assertTrue(result[0])

    @skipIf(CONDITION, REASON)
    def test_insert_user(self):
        # Create table and user
        self.hdd_db_handler.create_users_table()
        self.hdd_db_handler.insert_user(username=test_data.USERNAME,
                                        phone_number=test_data.PHONE_NUMBER,
                                        password=test_data.PASSWORD)
        # Get user from table
        query = 'SELECT * FROM users WHERE username = %s;'
        result = self.hdd_db_handler.cursor_execute(query, (test_data.USERNAME,))

        # Check query result
        if result:
            result = result.fetchone()
            user_id, username, phone, password = result

            self.assertEqual(user_id, test_data.USER_ID)
            self.assertEqual(username, test_data.USERNAME)
            self.assertEqual(phone, test_data.PHONE_NUMBER)
            self.assertEqual(password, test_data.PASSWORD)

        else:
            self.fail('User not found.')

    @skipIf(CONDITION, REASON)
    def test_insert_address(self):
        # Create table and user address
        self.hdd_db_handler.create_address_table()
        self.hdd_db_handler.insert_address(user_address=test_data.USER_ADDRESS)

        # Get address from table
        query = 'SELECT * FROM address;'
        result = self.hdd_db_handler.cursor_execute(query, ())

        # Check query result
        if result:
            result = result.fetchone()
            user_address, last_used = result

            self.assertEqual(user_address, test_data.USER_ADDRESS)
            self.assertTrue(isinstance(last_used, datetime))

        else:
            self.fail('User address not found.')

    @skipIf(CONDITION, REASON)
    def test_insert_user_address(self):
        # Create user, address, user_address tables
        self.hdd_db_handler.create_users_table()
        self.hdd_db_handler.create_address_table()
        self.hdd_db_handler.create_user_address_table()

        # Create user and address
        self.hdd_db_handler.insert_user(username=test_data.USERNAME,
                                        phone_number=test_data.PHONE_NUMBER,
                                        password=test_data.PASSWORD)
        self.hdd_db_handler.insert_address(user_address=test_data.USER_ADDRESS)

        # Create connection between user and address
        self.hdd_db_handler.insert_user_address(user_id=test_data.USER_ID,
                                                user_address=test_data.USER_ADDRESS)

        # Get user address data
        query = 'SELECT * FROM user_address;'
        result = self.hdd_db_handler.cursor_execute(query, ())

        # Check query result
        if result:
            result = result.fetchone()
            user_id, user_address = result

            self.assertEqual(user_id, test_data.USER_ID)
            self.assertEqual(user_address, test_data.USER_ADDRESS)

        else:
            self.fail('User id and user address not found.')

    @skipIf(CONDITION, REASON)
    def test_insert_user_token(self):
        # Create user, tokens tables
        self.hdd_db_handler.create_users_table()
        self.hdd_db_handler.create_tokens_table()

        # Create user
        self.hdd_db_handler.insert_user(username=test_data.USERNAME,
                                        phone_number=test_data.PHONE_NUMBER,
                                        password=test_data.PASSWORD)

        # Create token for user
        self.hdd_db_handler.insert_user_token(user_id=test_data.USER_ID,
                                              token=test_data.USER_TOKEN)

        # Get user token data
        query = 'SELECT * FROM tokens;'
        result = self.hdd_db_handler.cursor_execute(query, ())

        # Check query result
        if result:
            result = result.fetchone()
            user_id, token = result

            self.assertEqual(user_id, test_data.USER_ID)
            self.assertEqual(token, test_data.USER_TOKEN)

        else:
            self.fail('User id and user token not found.')

    @skipIf(CONDITION, REASON)
    def test_insert_user_public_key(self):
        # Create user, public keys tables
        self.hdd_db_handler.create_users_table()
        self.hdd_db_handler.create_public_keys_table()

        # Create user
        self.hdd_db_handler.insert_user(username=test_data.USERNAME,
                                        phone_number=test_data.PHONE_NUMBER,
                                        password=test_data.PASSWORD)

        # Create public key for user
        self.hdd_db_handler.insert_user_public_key(user_id=test_data.USER_ID,
                                                   public_key=test_data.USER_PUBLIC_KEY)

        # Get user public key data
        query = 'SELECT * FROM tokens;'
        result = self.hdd_db_handler.cursor_execute(query, ())

        # Check query result
        if result:
            result = result.fetchone()
            user_id, token = result

            self.assertEqual(user_id, test_data.USER_ID)
            self.assertEqual(token, test_data.USER_TOKEN)

        else:
            self.fail('User id and user public key not found.')

    @skipIf(CONDITION, REASON)
    def test_insert_message(self):
        # Create user, messages tables
        self.hdd_db_handler.create_users_table()
        self.hdd_db_handler.create_messages_table()

        # Create users
        self.hdd_db_handler.insert_user(username=test_data.USERNAME,
                                        phone_number=test_data.PHONE_NUMBER,
                                        password=test_data.PASSWORD)
        self.hdd_db_handler.insert_user(username=test_data.USERNAME_2,
                                        phone_number=test_data.PHONE_NUMBER_2,
                                        password=test_data.PASSWORD)

        # Create message for users
        test_message = 'test message'
        self.hdd_db_handler.insert_message(sender_id=test_data.USER_ID,
                                           receiver_id=test_data.USER_ID_2,
                                           sender_username=test_data.USERNAME,
                                           message=test_message)

        # Get message data
        query = 'SELECT * FROM messages;'
        result = self.hdd_db_handler.cursor_execute(query, ())

        # Check query result
        if result:
            result = result.fetchone()
            (message_id, user_sender_id, user_receiver_id, sender_username, message,
             receive_date) = result

            self.assertEqual(user_sender_id, test_data.USER_ID)
            self.assertEqual(user_receiver_id, test_data.USER_ID_2)
            self.assertEqual(sender_username, test_data.USERNAME)
            self.assertEqual(message, test_message)
            self.assertTrue(isinstance(receive_date, datetime))

        else:
            self.fail('Message data not found.')

    def tearDown(self):
        # Drop all tables in HDD database
        query = "select 'drop table if exists "' || tablename || '" cascade;' from pg_tables;"
        self.hdd_db_handler.cursor_with_commit(query, [])
