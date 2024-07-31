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

