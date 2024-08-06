import sqlite3
from unittest import TestCase
from server_side.database.sqlite_handler import RAMDatabaseHandler
from tests import test_data


RAM_TABLES = {'user_address': 'user_address', 'usernames': 'usernames',
              'tokens': 'tokens', 'public_keys': 'public_keys'}


class TestUser(TestCase):

    def setUp(self):
        self.ram_db_handler = RAMDatabaseHandler()

    def test_create_user_address_table(self):
        self.ram_db_handler.create_user_address_table()

        query = f"SELECT * FROM {RAM_TABLES['user_address']}"
        try:
            self.ram_db_handler.cursor.execute(query)
            self.assertTrue(True)

        except sqlite3.DatabaseError as e:
            self.assertFalse(f'no such table: {RAM_TABLES['user_address']}' in e.args[0])

    def test_create_usernames_table(self):
        self.ram_db_handler.create_usernames_table()

        query = f"SELECT * FROM {RAM_TABLES['usernames']}"
        try:
            self.ram_db_handler.cursor.execute(query)
            self.assertTrue(True)

        except sqlite3.DatabaseError as e:
            self.assertFalse(f"no such table: {RAM_TABLES['usernames']}" in e.args[0])

    def test_create_tokens_table(self):
        self.ram_db_handler.create_tokens_table()

        query = f"SELECT * FROM {RAM_TABLES['tokens']}"
        try:
            self.ram_db_handler.cursor.execute(query)
            self.assertTrue(True)

        except sqlite3.DatabaseError as e:
            self.assertFalse(f"no such table: {RAM_TABLES['tokens']}" in e.args[0])

    def test_create_public_keys_table(self):
        self.ram_db_handler.create_public_keys_table()

        query = f"SELECT * FROM {RAM_TABLES['public_keys']}"
        try:
            self.ram_db_handler.cursor.execute(query)
            self.assertTrue(True)

        except sqlite3.DatabaseError as e:
            self.assertFalse(f"no such table: {RAM_TABLES['public_keys']}" in e.args[0])

    def test_create_all_tables(self):
        self.ram_db_handler.create_all_tables()

        for table in RAM_TABLES:
            with self.subTest(f"Check '{table}' table", table=table):

                query = f"SELECT * FROM {table}"
                try:
                    self.ram_db_handler.cursor.execute(query)
                    self.assertTrue(True)

                except sqlite3.DatabaseError as e:
                    self.assertFalse(f"no such table: {table}" in e.args[0])

    def test_insert_user_address(self):
        self.ram_db_handler.create_user_address_table()
        self.ram_db_handler.insert_user_address(user_id=test_data.USER_ID,
                                                user_address=test_data.USER_ADDRESS)

        query = f"SELECT * FROM {RAM_TABLES['user_address']}"
        try:
            result = self.ram_db_handler.cursor.execute(query)
            self.assertTrue(result)

        except sqlite3.DatabaseError as e:
            self.fail(e)

    def test_insert_username(self):
        self.ram_db_handler.create_usernames_table()
        self.ram_db_handler.insert_username(user_id=test_data.USER_ID,
                                            username=test_data.USERNAME)

        query = f"SELECT * FROM {RAM_TABLES['usernames']}"
        try:
            result = self.ram_db_handler.cursor.execute(query)
            self.assertTrue(result)

        except sqlite3.DatabaseError as e:
            self.fail(e)

    def test_insert_user_token(self):
        self.ram_db_handler.create_tokens_table()
        self.ram_db_handler.insert_user_token(user_id=test_data.USER_ID,
                                              token=test_data.USER_TOKEN)

        query = f"SELECT * FROM {RAM_TABLES['tokens']}"
        try:
            result = self.ram_db_handler.cursor.execute(query)
            self.assertTrue(result)

        except sqlite3.DatabaseError as e:
            self.fail(e)

    def test_insert_user_public_key(self):
        self.ram_db_handler.create_public_keys_table()
        self.ram_db_handler.insert_user_token(user_id=test_data.USER_ID,
                                              token=test_data.USER_TOKEN)

        query = f"SELECT * FROM {RAM_TABLES['public_keys']}"
        try:
            result = self.ram_db_handler.cursor.execute(query)
            self.assertTrue(result)

        except sqlite3.DatabaseError as e:
            self.fail(e)

    def test_get_user(self):
        self.ram_db_handler.create_usernames_table()
        self.ram_db_handler.insert_username(user_id=test_data.USER_ID,
                                            username=test_data.USERNAME)

        # First case: get username data by user_id
        result = self.ram_db_handler.get_user(user_id=test_data.USER_ID)
        user_id, username = result
        self.assertEqual(user_id, test_data.USER_ID)
        self.assertEqual(username, test_data.USERNAME)

        # Second case: get username data by username
        result = self.ram_db_handler.get_user(username=test_data.USERNAME)
        user_id, username = result
        self.assertEqual(user_id, test_data.USER_ID)
        self.assertEqual(username, test_data.USERNAME)

        # Third case: get non-exits username
        result = self.ram_db_handler.get_user(username='Max Payne')
        self.assertTrue(result is None)

        # Fourth case: get non-exits user_id
        result = self.ram_db_handler.get_user(user_id=-1)
        self.assertTrue(result is None)

        # Fifth case: pass no vars
        result = self.ram_db_handler.get_user()
        self.assertTrue(result is None)

    def test_get_username(self):
        self.ram_db_handler.create_usernames_table()
        self.ram_db_handler.insert_username(user_id=test_data.USER_ID,
                                            username=test_data.USERNAME)

        # First case: get data by user_id
        username = self.ram_db_handler.get_username(user_id=test_data.USER_ID)
        self.assertEqual(username, test_data.USERNAME)

        # Second case: get non-exits username data
        username = self.ram_db_handler.get_username(user_id=-1)
        self.assertEqual(username, '')

    def test_get_user_id(self):
        self.ram_db_handler.create_usernames_table()
        self.ram_db_handler.insert_username(user_id=test_data.USER_ID,
                                            username=test_data.USERNAME)

        # First case: get username data by user_id
        user_id = self.ram_db_handler.get_user_id(username=test_data.USERNAME)
        self.assertEqual(user_id, test_data.USER_ID)

        # Second case: get username data by non-exists user_id
        user_id = self.ram_db_handler.get_user_id(username='Max Payne')
        self.assertTrue(user_id is None)

    def test_get_user_address(self):
        self.ram_db_handler.create_user_address_table()
        self.ram_db_handler.insert_user_address(user_id=test_data.USER_ID,
                                                user_address=test_data.USER_ADDRESS)

        # First case: get user address by user_id
        user_address_list = self.ram_db_handler.get_user_address(user_id=test_data.USER_ID)
        self.assertEqual(user_address_list, [test_data.USER_ADDRESS])

        # Second case: get non-exits user_id
        user_address_list = self.ram_db_handler.get_user_address(user_id=-1)
        self.assertEqual(user_address_list, [])

    def test_get_user_token(self):
        self.ram_db_handler.create_tokens_table()
        self.ram_db_handler.insert_user_token(user_id=test_data.USER_ID,
                                              token=test_data.USER_TOKEN)

        # First case: get user token by user_id
        user_token = self.ram_db_handler.get_user_token(user_id=test_data.USER_ID)
        self.assertEqual(user_token, test_data.USER_TOKEN)

        # Second case: get user token by non-exists user_id
        user_token = self.ram_db_handler.get_user_token(user_id=-1)
        self.assertTrue(user_token is None)

    def test_get_user_public_key(self):
        self.ram_db_handler.create_public_keys_table()
        self.ram_db_handler.insert_user_public_key(user_id=test_data.USER_ID,
                                                   public_key=test_data.USER_PUBLIC_KEY)

        # First case: get user public_key by user_id
        public_key = self.ram_db_handler.get_user_public_key(user_id=test_data.USER_ID)
        self.assertEqual(public_key, test_data.USER_PUBLIC_KEY)

        # Second case: get user public_key by non-exists user_id
        public_key = self.ram_db_handler.get_user_public_key(user_id=-1)
        self.assertTrue(public_key is None)

    def test_delete_user(self):
        self.ram_db_handler.create_usernames_table()
        self.ram_db_handler.insert_username(user_id=test_data.USER_ID,
                                            username=test_data.USERNAME)

        # First case: delete by user_id
        self.ram_db_handler.delete_user(user_id=test_data.USER_ID)
        user_id = self.ram_db_handler.get_user(user_id=test_data.USER_ID)
        self.assertTrue(user_id is None)

        # Second case: delete by username
        self.ram_db_handler.delete_user(username=test_data.USERNAME)
        user_id = self.ram_db_handler.get_user(username=test_data.USERNAME)
        self.assertTrue(user_id is None)

    def test_delete_user_address(self):
        self.ram_db_handler.create_user_address_table()
        self.ram_db_handler.insert_user_address(user_id=test_data.USER_ID,
                                                user_address=test_data.USER_ADDRESS)

        self.ram_db_handler.delete_user_address(user_id=test_data.USER_ID)
        user_address_list = self.ram_db_handler.get_user_address(user_id=test_data.USER_ID)
        self.assertEqual(user_address_list, [])

    def test_delete_user_token(self):
        self.ram_db_handler.create_tokens_table()
        self.ram_db_handler.insert_user_token(user_id=test_data.USER_ID,
                                              token=test_data.USER_TOKEN)

        self.ram_db_handler.delete_user_token(user_id=test_data.USER_ID)
        user_token = self.ram_db_handler.get_user_token(user_id=test_data.USER_ID)
        self.assertTrue(user_token is None)

    def test_delete_user_public_key(self):
        self.ram_db_handler.create_public_keys_table()
        self.ram_db_handler.insert_user_public_key(user_id=test_data.USER_ID,
                                                   public_key=test_data.USER_PUBLIC_KEY)

        self.ram_db_handler.delete_user_public_key(user_id=test_data.USER_ID)
        public_key = self.ram_db_handler.get_user_public_key(user_id=test_data.USER_ID)
        self.assertTrue(public_key is None)
