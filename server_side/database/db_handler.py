import os
import sqlite3


class DatabaseHandler:

    def __init__(self, database):
        self.conn = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.conn.cursor()

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

    def create_sessions_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions
            (user_id INTEGER NOT NULL UNIQUE,
            session_id TEXT NOT NULL,
            expiration_date DATETIME DEFAULT CURRENT_TIMESTAMP)
            ''')

    def create_user_address_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_address
            (id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            user_address TEXT NOT NULL UNIQUE,
            last_used DATETIME DEFAULT CURRENT_TIMESTAMP)
            ''')

    def insert_message(self, sender_id, receiver_id, sender_username, message):
        self.cursor.execute('INSERT INTO messages ("user_sender_id", "user_receiver_id", "sender_username", "message") '
                            'VALUES (?, ?, ?, ?)',
                            (sender_id, receiver_id, sender_username, message))
        self.conn.commit()

    def insert_session_id(self, user_id, session_id):
        self.cursor.execute('INSERT OR IGNORE INTO sessions ("user_id", "session_id") VALUES (?, ?)',
                            (user_id, session_id))
        self.conn.commit()

    def get_user_messages(self, receiver_id):
        result = self.cursor.execute('SELECT * FROM messages WHERE user_receiver_id = ?',
                                     (receiver_id,))
        return result.fetchall()

    def delete_user_messages(self, receiver_id):
        self.cursor.execute('DELETE FROM messages WHERE user_receiver_id = ?', (receiver_id,))
        self.conn.commit()

    def delete_messages(self, message_ids):
        self.cursor.execute('DELETE FROM messages WHERE id IN (?)', (message_ids,))
        self.conn.commit()

    def get_user_address(self, user_id):
        result = self.cursor.execute('SELECT user_address FROM user_address WHERE user_id = ?',
                                     (user_id,))
        return [item[0] for item in result.fetchall()]  # convert tuple to string

    def get_user_session(self, user_id):
        result = self.cursor.execute('SELECT session_id FROM sessions WHERE user_id = ?',
                                     (user_id,))
        result = result.fetchone()
        if result:
            return result[0]

    def insert_user_address(self, user_id, user_address):
        self.cursor.execute('INSERT OR IGNORE INTO user_address ("user_id", "user_address") '
                            'VALUES (?, ?)',
                            (user_id, user_address))
        self.conn.commit()

    def insert_user(self, username, phone_number, password='qwerty'):
        if self.is_user_exists(username=username):
            return

        if self.is_phone_exists(phone_number):
            return

        self.cursor.execute('INSERT INTO users ("username", "phone", "password") VALUES (?, ?, ?)',
                            (username, phone_number, password))
        self.conn.commit()

    def get_user_password(self, username):
        result = self.cursor.execute('SELECT password FROM users WHERE username = ?',
                                     (username,))
        result = result.fetchone()
        if result:
            return result[0]

    def get_user_id_by_username(self, username):
        result = self.cursor.execute('SELECT id FROM users WHERE username = ?',
                                     (username,))
        result = result.fetchone()
        if result:
            return result[0]

    def is_user_exists(self, user_id=None, username=None):
        if user_id:
            result = self.cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
            if result.fetchall():
                return True

        elif username:
            result = self.cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
            if result.fetchall():
                return True

        else:
            return False

    def is_phone_exists(self, phone_number):
        result = self.cursor.execute('SELECT phone FROM users WHERE username = ?', (phone_number,))
        if result.fetchall():
            return True
        else:
            return False

    def __del__(self):
        self.cursor.close()
        self.conn.close()


class RAMDatabaseHandler(DatabaseHandler):

    def __init__(self):
        super().__init__(':memory:')

    def create_all_tables(self):
        self.create_sessions_table()
        self.create_user_address_table()


class HDDDatabaseHandler(DatabaseHandler):

    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, 'database.sqlite')
        super().__init__(db_path)

    def create_all_tables(self):
        self.create_users_table()
        self.create_user_address_table()


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
    ram_handler.create_sessions_table()

    ram_handler.insert_user_address(1, 'http://127.0.0.1:6666')
    ram_handler.insert_user_address(2, 'http://127.0.0.1:7777')

    ram_handler.insert_message(1, 2, 'user_1', 'test')
    ram_handler.insert_message(1, 2, 'user_1', 'test1')
    ram_handler.insert_message(1, 2, 'user_1', 'test2')

    ram_handler.insert_session_id(1, '123')

    print(ram_handler.get_user_messages(2))
    print(ram_handler.get_user_session(1))

