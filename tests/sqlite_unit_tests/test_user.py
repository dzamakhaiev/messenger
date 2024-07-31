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

        table_query = f"SELECT * FROM {RAM_TABLES['user_address']}"
        try:
            self.ram_db_handler.cursor.execute(table_query)
            self.assertTrue(True)

        except sqlite3.DatabaseError as e:
            self.assertFalse(f'no such table: {RAM_TABLES['user_address']}' in e.args[0])

    def test_create_usernames_table(self):
        self.ram_db_handler.create_usernames_table()

        table_query = f"SELECT * FROM {RAM_TABLES['usernames']}"
        try:
            self.ram_db_handler.cursor.execute(table_query)
            self.assertTrue(True)

        except sqlite3.DatabaseError as e:
            self.assertFalse(f"no such table: {RAM_TABLES['usernames']}" in e.args[0])

    def test_create_tokens_table(self):
        self.ram_db_handler.create_tokens_table()

        table_query = f"SELECT * FROM {RAM_TABLES['tokens']}"
        try:
            self.ram_db_handler.cursor.execute(table_query)
            self.assertTrue(True)

        except sqlite3.DatabaseError as e:
            self.assertFalse(f"no such table: {RAM_TABLES['tokens']}" in e.args[0])

    def test_create_public_keys_table(self):
        self.ram_db_handler.create_public_keys_table()

        table_query = f"SELECT * FROM {RAM_TABLES['public_keys']}"
        try:
            self.ram_db_handler.cursor.execute(table_query)
            self.assertTrue(True)

        except sqlite3.DatabaseError as e:
            self.assertFalse(f"no such table: {RAM_TABLES['public_keys']}" in e.args[0])