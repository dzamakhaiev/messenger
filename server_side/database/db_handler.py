import os
import sqlite3
from time import sleep
from threading import Lock
from datetime import datetime, timedelta
from server_side.logger.logger import Logger

database_logger = Logger('database')
global_lock = Lock()
MIN_REQUEST_INTERVAL = timedelta(microseconds=10000)


class DatabaseHandler:

    last_request_time = datetime.now()

    def __init__(self, database):
        try:
            self.conn = sqlite3.connect(database, check_same_thread=False)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            quit(e)

    def check_min_request_interval(self):
        # Sleep to resolve bottleneck issue
        now = datetime.now()
        delta = now - self.last_request_time

        if delta < MIN_REQUEST_INTERVAL:
            seconds = MIN_REQUEST_INTERVAL.microseconds / 10 ** 6
            sleep(seconds)

        self.last_request_time = datetime.now()

    def cursor_with_lock(self, query, args):
        try:
            database_logger.debug(f'Execute query:\n{query}\nArgs:\n{args}')
            global_lock.acquire(True)
            self.check_min_request_interval()
            result = self.cursor.execute(query, args)

        finally:
            global_lock.release()

        return result

    def cursor_with_commit(self, query, args=None, many=False):
        database_logger.debug(f'Execute query:\n{query}\nArgs:\n{args}')
        if args is None:
            args = []

        if many:
            self.cursor.executemany(query, args)
        else:
            self.cursor.execute(query, args)

        self.conn.commit()

    def create_users_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL)
            ''')

    def create_messages_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_sender_id INTEGER NOT NULL,
            user_receiver_id INTEGER NOT NULL,
            sender_username TEXT NOT NULL,
            message TEXT NOT NULL,
            receive_date DATETIME DEFAULT CURRENT_TIMESTAMP)
            ''')

    def create_user_address_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_address
            (id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            user_address TEXT NOT NULL,
            last_used DATETIME DEFAULT CURRENT_TIMESTAMP)
            ''')

    def get_user(self, user_id=None, username=None):
        if user_id:
            result = self.cursor_with_lock('SELECT id, username FROM users WHERE id = ?', (user_id,))
        elif username:
            result = self.cursor_with_lock('SELECT id, username FROM users WHERE username = ?', (username,))
        else:
            return

        result = result.fetchone()
        if result:
            return result

    def get_user_messages(self, receiver_id):
        result = self.cursor_with_lock('SELECT * FROM messages WHERE user_receiver_id = ?',
                                       (receiver_id,))
        return result.fetchall()

    def get_user_password(self, username):
        result = self.cursor_with_lock('SELECT password FROM users WHERE username = ?',
                                       (username,))
        result = result.fetchone()
        if result:
            return result[0]

    def get_username(self, user_id):
        result = self.cursor_with_lock('SELECT username FROM users WHERE id = ?', (user_id,))
        result = result.fetchone()
        if result:
            return result[0]
        else:
            return ''

    def get_user_id(self, username):
        result = self.cursor_with_lock('SELECT id FROM users WHERE username = ?', (username,))
        result = result.fetchone()
        if result:
            return result[0]
        else:
            return None

    def get_user_address(self, user_id):
        result = self.cursor_with_lock('SELECT user_address FROM user_address WHERE user_id = ?',
                                       (user_id,))
        return [item[0] for item in result.fetchall()]  # convert tuple to string

    def get_all_messages(self):
        result = self.cursor_with_lock('SELECT user_sender_id, user_receiver_id, '
                                       'sender_username, message, receive_date '
                                       'FROM messages;', ())
        return result.fetchall()

    def check_user_address(self, user_id, user_address):
        result = self.cursor_with_lock('SELECT user_id FROM user_address WHERE user_id=? AND user_address=?',
                                       (user_id, user_address))
        result = result.fetchone()
        if result:
            return True
        else:
            return False

    def insert_user_address(self, user_id, user_address):
        if not self.check_user_address(user_id, user_address):
            self.cursor_with_commit('INSERT OR IGNORE INTO user_address ("user_id", "user_address") VALUES (?, ?)',
                                    (user_id, user_address))

    def insert_user(self, username, phone_number, password='qwerty'):
        self.cursor_with_commit('INSERT OR IGNORE INTO users ("username", "phone", "password") VALUES (?, ?, ?)',
                                (username, phone_number, password))

    def insert_message(self, sender_id, receiver_id, sender_username, message):
        self.cursor_with_commit('INSERT INTO messages '
                                '("user_sender_id", "user_receiver_id", "sender_username", "message") '
                                'VALUES (?, ?, ?, ?)',
                                (sender_id, receiver_id, sender_username, message))

    def insert_messages(self, messages):
        self.cursor_with_commit('INSERT INTO messages ('
                                '"user_sender_id", "user_receiver_id", "sender_username", "message", "receive_date") '
                                'VALUES (?, ?, ?, ?, ?)', messages, many=True)

    def delete_user_messages(self, receiver_id):
        self.cursor_with_commit('DELETE FROM messages WHERE user_receiver_id = ?', (receiver_id,))

    def delete_messages(self, message_ids):
        self.cursor_with_commit('DELETE FROM messages WHERE id IN (?)', (message_ids,))

    def delete_all_messages(self):
        self.cursor_with_commit('DELETE FROM messages')

    def delete_user(self, user_id=None, username=None):
        if user_id:
            self.cursor_with_commit('DELETE FROM users WHERE id = ?', (user_id,))
        elif username:
            self.cursor_with_commit('DELETE FROM users WHERE username = ?', (username,))

    def __del__(self):
        if self.conn and self.cursor:
            self.cursor.close()
            self.conn.close()
        database_logger.info('Connection closed.')


class RAMDatabaseHandler(DatabaseHandler):

    def __init__(self):
        database_logger.info('SQLite in-memory connection opened.')
        super().__init__(':memory:')

    def create_all_tables(self):
        self.create_messages_table()
        self.create_usernames_table()
        self.create_user_address_table()

    def create_usernames_table(self):
        self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS usernames
                    (user_id INTEGER UNIQUE,
                    username TEXT NOT NULL UNIQUE)
                    ''')

    def insert_username(self, user_id, username):
        self.cursor_with_commit('INSERT OR IGNORE INTO usernames ("user_id", "username") VALUES (?, ?)',
                                (user_id, username))

    def get_user(self, user_id=None, username=None):
        if user_id:
            result = self.cursor_with_lock('SELECT * FROM usernames WHERE user_id = ?', (user_id,))
        elif username:
            result = self.cursor_with_lock('SELECT * FROM usernames WHERE username = ?', (username,))
        else:
            return

        result = result.fetchone()
        if result:
            return result

    def get_username(self, user_id):
        result = self.cursor_with_lock('SELECT username FROM usernames WHERE user_id = ?', (user_id,))
        result = result.fetchone()
        if result:
            return result[0]
        else:
            return ''

    def get_user_id(self, username):
        result = self.cursor_with_lock('SELECT user_id FROM usernames WHERE username = ?', (username,))
        result = result.fetchone()
        if result:
            return result[0]
        else:
            return

    def delete_user(self, user_id=None, username=None):
        if user_id:
            self.cursor_with_commit('DELETE FROM usernames WHERE user_id = ?', (user_id,))
        elif username:
            self.cursor_with_commit('DELETE FROM usernames WHERE username = ?', (username,))


class HDDDatabaseHandler(DatabaseHandler):

    def __init__(self):
        database_logger.info('SQLite connection opened.')
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, 'database.sqlite')
        super().__init__(db_path)

    def create_all_tables(self):
        database_logger.info('Create tables.')
        self.create_users_table()
        self.create_user_address_table()
        self.create_messages_table()

        # Add test users
        database_logger.info('Create test users.')
        self.insert_user('user_1', '123456789')
        self.insert_user('user_2', '987654321')


if __name__ == '__main__':
    handler = HDDDatabaseHandler()
    handler.create_users_table()
    handler.create_user_address_table()

    # Add test users
    handler.insert_user('user_1', '123456789')
    handler.insert_user('user_2', '987654321')

    ram_handler = RAMDatabaseHandler()
    ram_handler.create_messages_table()
    ram_handler.create_user_address_table()

    ram_handler.insert_user_address(1, 'http://127.0.0.1:6666')
    ram_handler.insert_user_address(2, 'http://127.0.0.1:7777')

    ram_handler.insert_message(1, 2, 'user_1', 'test')
    ram_handler.insert_message(1, 2, 'user_1', 'test1')
    ram_handler.insert_message(1, 2, 'user_1', 'test2')
    print(ram_handler.get_user_messages(2))
