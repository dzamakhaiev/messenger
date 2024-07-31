import sqlite3
from unittest import TestCase
from server_side.database.sqlite_handler import RAMDatabaseHandler

from tests import test_data


class TestUser(TestCase):

    def setUp(self):
        self.ram_db_handler = RAMDatabaseHandler()

    def test_create_user_address_table(self):
        self.ram_db_handler.create_user_address_table()

        table_query = "SELECT * FROM user_address"
        try:
            self.ram_db_handler.cursor.execute(table_query)
            self.assertTrue(True)

        except sqlite3.DatabaseError as e:
            self.assertFalse('no such table: user_address' in e.args[0])

    def test_create_usernames_table(self):
        self.ram_db_handler.create_usernames_table()

        table_query = "SELECT * FROM usernames"
        try:
            self.ram_db_handler.cursor.execute(table_query)
            self.assertTrue(True)

        except sqlite3.DatabaseError as e:
            self.assertFalse('no such table: usernames' in e.args[0])

    def test_create_tokens_table(self):
        self.ram_db_handler.create_tokens_table()

        table_query = "SELECT * FROM tokens"
        try:
            self.ram_db_handler.cursor.execute(table_query)
            self.assertTrue(True)

        except sqlite3.DatabaseError as e:
            self.assertFalse('no such table: tokens' in e.args[0])

    def test_create_public_keys_table(self):
        self.ram_db_handler.create_public_keys_table()

        table_query = "SELECT * FROM public_keys"
        try:
            self.ram_db_handler.cursor.execute(table_query)
            self.assertTrue(True)

        except sqlite3.DatabaseError as e:
            self.assertFalse('no such table: public_keys' in e.args[0])