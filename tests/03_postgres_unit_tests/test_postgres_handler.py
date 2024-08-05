import os
from datetime import datetime
from unittest import TestCase, skipIf
from server_side.database.postgres_handler import PostgresHandler
from scripts.get_container_info import docker_is_running, container_is_running
from logger.logger import Logger
from tests import test_data


postgres_test_logger = Logger('postgres_test_logger')


RUN_INSIDE_DOCKER = int(os.environ.get('RUN_INSIDE_DOCKER', 0))
CI_RUN = int(os.environ.get('CI_RUN', 0))
CONTAINER_NAME = 'postgres-ci' if CI_RUN else 'postgres'
DOCKER_RUNNING = docker_is_running()
CONTAINER_RUNNING = container_is_running(CONTAINER_NAME)
CONDITION = not (DOCKER_RUNNING and CONTAINER_RUNNING)
REASON = f'Docker/{CONTAINER_NAME} container is not running'
WAIT_MESSAGE_TIME = 0.3


postgres_test_logger.info(f'Postgres unit tests.\n'
                          f'Run inside docker: {RUN_INSIDE_DOCKER}\n'
                          f'Continuous Integration: {CI_RUN}\n'
                          f'Condition for skip tests: {CONDITION}')


class TestPostgres(TestCase):

    def setUp(self):
        self.hdd_db_handler = PostgresHandler()
        self.drop_all_tables()
        query = 'GRANT ALL ON SCHEMA public TO postgres; GRANT ALL ON SCHEMA public TO public;'
        self.hdd_db_handler.cursor_with_commit(query, ())

    def drop_all_tables(self):
        # Drop all tables in HDD database
        postgres_test_logger.info('tearDown: delete all tables.')
        query = "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
        self.hdd_db_handler.cursor_with_commit(query, [])

    def create_user_table_and_user(self, user_number=1):
        # Create table and user
        self.hdd_db_handler.create_users_table()
        self.hdd_db_handler.insert_user(username=test_data.USERNAME,
                                        phone_number=test_data.PHONE_NUMBER,
                                        password=test_data.PASSWORD)
        if user_number == 2:
            self.hdd_db_handler.insert_user(username=test_data.USERNAME_2,
                                            phone_number=test_data.PHONE_NUMBER_2,
                                            password=test_data.PASSWORD)

    def create_address_table_and_address(self):
        # Create address table and user address
        self.hdd_db_handler.create_address_table()
        self.hdd_db_handler.insert_address(user_address=test_data.USER_ADDRESS)

    def create_user_address_table_and_connection(self):
        # Create users, address, user_address tables and
        # user, address items, and connection between them
        self.create_user_table_and_user()
        self.create_address_table_and_address()
        self.hdd_db_handler.create_user_address_table()
        self.hdd_db_handler.insert_user_address(user_id=test_data.USER_ID,
                                                user_address=test_data.USER_ADDRESS)

    def create_user_token_table_and_connection(self):
        # Create users, tokens tables and
        # user, token, and connection between them
        self.create_user_table_and_user()
        self.hdd_db_handler.create_tokens_table()
        self.hdd_db_handler.insert_user_token(user_id=test_data.USER_ID,
                                              token=test_data.USER_TOKEN)

    def create_user_public_keys_table_and_connection(self):
        # Create users, public_keys tables and
        # user, public_key, and connection between them
        self.create_user_table_and_user()
        self.hdd_db_handler.create_public_keys_table()
        self.hdd_db_handler.insert_user_public_key(user_id=test_data.USER_ID,
                                                   public_key=test_data.USER_PUBLIC_KEY)

    def create_messages_table_and_message(self, test_message='test message'):
        # Create user, messages tables and
        # user, message, and connection between them
        self.create_user_table_and_user(user_number=2)
        self.hdd_db_handler.create_messages_table()
        self.hdd_db_handler.insert_message(sender_id=test_data.USER_ID,
                                           receiver_id=test_data.USER_ID_2,
                                           sender_username=test_data.USERNAME,
                                           message=test_message)

    def check_message(self, result, test_message):
        if result and isinstance(result, tuple):
            (message_id, user_sender_id, user_receiver_id, sender_username, message,
             receive_date) = result

        elif result := result.fetchone():
            (message_id, user_sender_id, user_receiver_id, sender_username, message,
             receive_date) = result

        else:
            self.fail(f'Incorrect message data: {result}')

        self.assertEqual(user_sender_id, test_data.USER_ID)
        self.assertEqual(user_receiver_id, test_data.USER_ID_2)
        self.assertEqual(sender_username, test_data.USERNAME)
        self.assertEqual(message, test_message)
        self.assertTrue(isinstance(receive_date, datetime))

    @skipIf(CONDITION, REASON)
    def test_create_users_table(self):
        self.hdd_db_handler.create_users_table()

        query = 'SELECT EXISTS(SELECT relname FROM pg_class WHERE relname = %s)'
        result = self.hdd_db_handler.cursor_execute(query, ('users',))
        result = result.fetchone()
        self.assertTrue(result[0])

    @skipIf(CONDITION, REASON)
    def test_create_messages_table(self):
        self.hdd_db_handler.create_users_table()  # related to "users" tables
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
        self.hdd_db_handler.create_users_table()  # related to "users" tables
        self.hdd_db_handler.create_address_table()  # related to "address" tables
        self.hdd_db_handler.create_user_address_table()

        query = 'SELECT EXISTS(SELECT relname FROM pg_class WHERE relname = %s)'
        result = self.hdd_db_handler.cursor_execute(query, ('user_address',))
        result = result.fetchone()
        self.assertTrue(result[0])

    @skipIf(CONDITION, REASON)
    def test_create_tokens_table(self):
        self.hdd_db_handler.create_users_table()  # related to "users" tables
        self.hdd_db_handler.create_tokens_table()

        query = 'SELECT EXISTS(SELECT relname FROM pg_class WHERE relname = %s)'
        result = self.hdd_db_handler.cursor_execute(query, ('tokens',))
        result = result.fetchone()
        self.assertTrue(result[0])

    @skipIf(CONDITION, REASON)
    def test_create_public_keys_table(self):
        self.hdd_db_handler.create_users_table()  # related to "users" tables
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
        if result := result.fetchone():
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
        if result := result.fetchone():
            user_address, last_used = result

            self.assertEqual(user_address, test_data.USER_ADDRESS)
            self.assertTrue(isinstance(last_used, datetime))

        else:
            self.fail('User address not found.')

    @skipIf(CONDITION, REASON)
    def test_insert_user_address(self):
        # Create user, address, user_address tables
        self.create_user_table_and_user()
        self.create_address_table_and_address()
        self.hdd_db_handler.create_user_address_table()

        # Create connection between user and address
        self.hdd_db_handler.insert_user_address(user_id=test_data.USER_ID,
                                                user_address=test_data.USER_ADDRESS)

        # Get user address data
        query = 'SELECT * FROM user_address;'
        result = self.hdd_db_handler.cursor_execute(query, ())

        # Check query result
        if result := result.fetchone():
            user_id, user_address = result

            self.assertEqual(user_id, test_data.USER_ID)
            self.assertEqual(user_address, test_data.USER_ADDRESS)

        else:
            self.fail('User id and user address not found.')

    @skipIf(CONDITION, REASON)
    def test_insert_user_token(self):
        # Create user, tokens tables
        self.create_user_table_and_user()
        self.hdd_db_handler.create_tokens_table()

        # Create token for user
        self.hdd_db_handler.insert_user_token(user_id=test_data.USER_ID,
                                              token=test_data.USER_TOKEN)

        # Get user token data
        query = 'SELECT * FROM tokens;'
        result = self.hdd_db_handler.cursor_execute(query, ())

        # Check query result
        if result := result.fetchone():
            user_id, token = result

            self.assertEqual(user_id, test_data.USER_ID)
            self.assertEqual(token, test_data.USER_TOKEN)

        else:
            self.fail('User id and user token not found.')

    @skipIf(CONDITION, REASON)
    def test_insert_user_public_key(self):
        # Create user, public keys tables
        self.create_user_table_and_user()
        self.hdd_db_handler.create_public_keys_table()

        # Create public key for user
        self.hdd_db_handler.insert_user_public_key(user_id=test_data.USER_ID,
                                                   public_key=test_data.USER_PUBLIC_KEY)

        # Get user public key data
        query = 'SELECT * FROM public_keys;'
        result = self.hdd_db_handler.cursor_execute(query, ())

        # Check query result
        if result := result.fetchone():
            user_id, token, create_date = result

            self.assertEqual(user_id, test_data.USER_ID)
            self.assertEqual(token, test_data.USER_PUBLIC_KEY)
            self.assertTrue(isinstance(create_date, datetime))

        else:
            self.fail('User id and user public key not found.')

    @skipIf(CONDITION, REASON)
    def test_insert_message(self):
        # Create user, messages tables
        self.create_user_table_and_user(user_number=2)
        self.hdd_db_handler.create_messages_table()

        # Create message for users
        test_message = 'test message'
        self.hdd_db_handler.insert_message(sender_id=test_data.USER_ID,
                                           receiver_id=test_data.USER_ID_2,
                                           sender_username=test_data.USERNAME,
                                           message=test_message)

        # Get message data
        query = 'SELECT * FROM messages;'
        result = self.hdd_db_handler.cursor_execute(query, ())

        # Check query resul
        self.check_message(result, test_message)

    @skipIf(CONDITION, REASON)
    def test_insert_messages(self):
        # Create user, messages tables
        self.create_user_table_and_user(user_number=2)
        self.hdd_db_handler.create_messages_table()

        # Create message list for users
        test_message = 'test message'
        message_item = [test_data.USER_ID, test_data.USER_ID_2, test_data.USERNAME,
                        test_message, datetime.now()]
        test_messages = [message_item]
        self.hdd_db_handler.insert_messages(messages=test_messages)

        # Get message data
        query = 'SELECT * FROM messages;'
        result = self.hdd_db_handler.cursor_execute(query, ())

        # Check query result
        self.check_message(result, test_message)

    @skipIf(CONDITION, REASON)
    def test_get_user(self):
        self.hdd_db_handler.create_users_table()

        # First case: no user in table
        user = self.hdd_db_handler.get_user(user_id=test_data.USER_ID)
        self.assertTrue(user is None)

        # Create user
        self.create_user_table_and_user()

        # Second case: user in table. Get by user_id
        user = self.hdd_db_handler.get_user(user_id=test_data.USER_ID)
        user_id, username = user
        self.assertEqual(user_id, test_data.USER_ID)
        self.assertEqual(username, test_data.USERNAME)

        # Third case: user in table. Get by username
        user = self.hdd_db_handler.get_user(username=test_data.USERNAME)
        user_id, username = user
        self.assertEqual(user_id, test_data.USER_ID)
        self.assertEqual(username, test_data.USERNAME)

        # Forth case: pass no variables
        user = self.hdd_db_handler.get_user()
        self.assertTrue(user is None)

    @skipIf(CONDITION, REASON)
    def test_get_user_address(self):
        self.hdd_db_handler.create_users_table()
        self.hdd_db_handler.create_address_table()
        self.hdd_db_handler.create_user_address_table()

        # First case: no user address in table
        address_list = self.hdd_db_handler.get_user_address(user_id=test_data.USER_ID)
        self.assertEqual(address_list, [])

        # Create user, address and connect them
        self.create_user_address_table_and_connection()

        # Second case: user address in table
        address_list = self.hdd_db_handler.get_user_address(user_id=test_data.USER_ID)
        self.assertEqual(address_list, [test_data.USER_ADDRESS])

    @skipIf(CONDITION, REASON)
    def test_get_user_messages(self):
        self.create_user_table_and_user(user_number=2)
        self.hdd_db_handler.create_messages_table()

        # First case: no message in table
        messages = self.hdd_db_handler.get_user_messages(receiver_id=test_data.USER_ID_2)
        self.assertEqual(messages, [])

        # Create message
        test_message = 'test_message'
        self.create_messages_table_and_message(test_message)

        # Second case: message in table and wrong user_id
        messages = self.hdd_db_handler.get_user_messages(receiver_id=test_data.USER_ID)
        self.assertEqual(messages, [])

        # Third case: message in table and correct user_id
        messages = self.hdd_db_handler.get_user_messages(receiver_id=test_data.USER_ID_2)
        self.check_message(messages[0], test_message)

    @skipIf(CONDITION, REASON)
    def test_get_all_messages(self):
        self.create_user_table_and_user(user_number=2)
        self.hdd_db_handler.create_messages_table()

        # First case: no message in table
        messages = self.hdd_db_handler.get_all_messages()
        self.assertEqual(messages, [])

        # Create message
        test_message = 'test_message'
        self.create_messages_table_and_message(test_message)

        # Second case: message in table and correct user_id
        messages = self.hdd_db_handler.get_all_messages()
        self.check_message(messages[0], test_message)

    @skipIf(CONDITION, REASON)
    def test_get_user_password(self):
        self.hdd_db_handler.create_users_table()

        # First case: no user in table
        password = self.hdd_db_handler.get_user_password(test_data.USERNAME)
        self.assertTrue(password is None)

        # Create user
        self.create_user_table_and_user()

        # Second case: user in table
        password = self.hdd_db_handler.get_user_password(test_data.USERNAME)
        self.assertEqual(password, test_data.PASSWORD)

    @skipIf(CONDITION, REASON)
    def test_get_username(self):
        self.hdd_db_handler.create_users_table()

        # First case: no user in table
        username = self.hdd_db_handler.get_username(user_id=test_data.USER_ID)
        self.assertEqual(username, '')

        # Create user
        self.create_user_table_and_user()

        # Second case: user in table
        username = self.hdd_db_handler.get_username(user_id=test_data.USER_ID)
        self.assertEqual(username, test_data.USERNAME)

    @skipIf(CONDITION, REASON)
    def test_get_user_id(self):
        self.hdd_db_handler.create_users_table()

        # First case: no user in table
        user_id = self.hdd_db_handler.get_user_id(username=test_data.USERNAME)
        self.assertTrue(user_id is None)

        # Create user
        self.create_user_table_and_user()

        # Second case: user in table
        user_id = self.hdd_db_handler.get_user_id(username=test_data.USERNAME)
        self.assertEqual(user_id, test_data.USER_ID)

    @skipIf(CONDITION, REASON)
    def test_get_user_token(self):
        self.create_user_table_and_user()
        self.hdd_db_handler.create_tokens_table()

        # First case: no token in table
        token = self.hdd_db_handler.get_user_token(user_id=test_data.USER_ID)
        self.assertTrue(token is None)

        # Create token for user
        self.create_user_token_table_and_connection()

        # Second case: token in table
        token = self.hdd_db_handler.get_user_token(user_id=test_data.USER_ID)
        self.assertEqual(token, test_data.USER_TOKEN)

    @skipIf(CONDITION, REASON)
    def test_get_user_public_key(self):
        self.create_user_table_and_user()
        self.hdd_db_handler.create_public_keys_table()

        # First case: no public_key in table
        public_key = self.hdd_db_handler.get_user_public_key(user_id=test_data.USER_ID)
        self.assertTrue(public_key is None)

        # Create token for user
        self.create_user_public_keys_table_and_connection()

        # Second case: user in table
        public_key = self.hdd_db_handler.get_user_public_key(user_id=test_data.USER_ID)
        self.assertEqual(public_key, test_data.USER_PUBLIC_KEY)

    @skipIf(CONDITION, REASON)
    def test_check_user_address(self):
        self.hdd_db_handler.create_users_table()
        self.hdd_db_handler.create_address_table()
        self.hdd_db_handler.create_user_address_table()

        # First case: no user address in table
        result = self.hdd_db_handler.check_user_address(user_id=test_data.USER_ID,
                                                        user_address=test_data.USER_ADDRESS)
        self.assertFalse(result)

        # Create user address connection
        self.create_user_address_table_and_connection()

        # Second case: user in table
        result = self.hdd_db_handler.check_user_address(user_id=test_data.USER_ID,
                                                        user_address=test_data.USER_ADDRESS)
        self.assertTrue(result)

    @skipIf(CONDITION, REASON)
    def test_delete_all_messages(self):
        # Create table and message
        self.create_messages_table_and_message()

        # Check that message exists
        messages = self.hdd_db_handler.get_user_messages(receiver_id=test_data.USER_ID_2)
        self.assertTrue(messages)

        # Delete all messages from table
        self.hdd_db_handler.delete_all_messages()

        messages = self.hdd_db_handler.get_user_messages(receiver_id=test_data.USER_ID_2)
        self.assertEqual(messages, [])

    @skipIf(CONDITION, REASON)
    def test_delete_messages(self):
        # Create table and message
        self.create_messages_table_and_message()

        # Check that message exists
        messages = self.hdd_db_handler.get_user_messages(receiver_id=test_data.USER_ID_2)
        self.assertTrue(messages)

        # Delete messages with ids from table
        self.hdd_db_handler.delete_messages(str(test_data.MESSAGE_ID))

        messages = self.hdd_db_handler.get_user_messages(receiver_id=test_data.USER_ID_2)
        self.assertEqual(messages, [])

    @skipIf(CONDITION, REASON)
    def test_delete_user_messages(self):
        # Create table and message
        self.create_messages_table_and_message()

        # Check that message exists
        messages = self.hdd_db_handler.get_user_messages(receiver_id=test_data.USER_ID_2)
        self.assertTrue(messages)

        # Delete all messages with receiver_id from table
        self.hdd_db_handler.delete_user_messages(receiver_id=test_data.USER_ID_2)

        messages = self.hdd_db_handler.get_user_messages(receiver_id=test_data.USER_ID_2)
        self.assertEqual(messages, [])

    @skipIf(CONDITION, REASON)
    def test_delete_user(self):
        self.create_user_table_and_user()

        # First case: delete by user_id
        self.hdd_db_handler.delete_user(user_id=test_data.USER_ID)
        user = self.hdd_db_handler.get_user(user_id=test_data.USER_ID)
        self.assertTrue(user is None)

        self.create_user_table_and_user()

        # Second case: delete by username
        self.hdd_db_handler.delete_user(username=test_data.USERNAME)
        user = self.hdd_db_handler.get_user(username=test_data.USERNAME)
        self.assertTrue(user is None)

        self.create_user_table_and_user()

        # Third case: call without variables. User will not be deleted
        self.hdd_db_handler.delete_user()
        user = self.hdd_db_handler.get_user(username=test_data.USERNAME)
        self.assertTrue(user)

    @skipIf(CONDITION, REASON)
    def test_delete_user_token(self):
        self.create_user_token_table_and_connection()

        # Check that token created
        token = self.hdd_db_handler.get_user_token(user_id=test_data.USER_ID)
        self.assertTrue(token)

        # Delete token
        self.hdd_db_handler.delete_user_token(user_id=test_data.USER_ID)
        token = self.hdd_db_handler.get_user_token(user_id=test_data.USER_ID)
        self.assertTrue(token is None)

    @skipIf(CONDITION, REASON)
    def test_delete_user_public_key(self):
        self.create_user_public_keys_table_and_connection()

        # Check that public key created
        public_key = self.hdd_db_handler.get_user_public_key(user_id=test_data.USER_ID)
        self.assertTrue(public_key)

        # Delete public key
        self.hdd_db_handler.delete_user_public_key(user_id=test_data.USER_ID)
        public_key = self.hdd_db_handler.get_user_public_key(user_id=test_data.USER_ID)
        self.assertTrue(public_key is None)

    @skipIf(CONDITION, REASON)
    def test_delete_user_address(self):
        self.create_user_address_table_and_connection()

        # Check that user address in table
        result = self.hdd_db_handler.check_user_address(user_id=test_data.USER_ID,
                                                        user_address=test_data.USER_ADDRESS)
        self.assertTrue(result)

        # Delete user address
        self.hdd_db_handler.delete_user_address(user_id=test_data.USER_ID)
        result = self.hdd_db_handler.check_user_address(user_id=test_data.USER_ID,
                                                        user_address=test_data.USER_ADDRESS)
        self.assertFalse(result)

    def tearDown(self):
        self.drop_all_tables()
