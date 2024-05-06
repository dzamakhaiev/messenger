import os
import sqlite3


class RAMDatabaseHandler:

    def __init__(self):

        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

    def create_messages_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_sender_id INTEGER NOT NULL,
            user_receiver_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL,
            receive_date DATETIME DEFAULT CURRENT_TIMESTAMP)
            ''')

    def create_user_address_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_address
            (id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            user_url TEXT NOT NULL,
            status TEXT DEFAULT "Active",
            last_used DATETIME DEFAULT CURRENT_TIMESTAMP)
            ''')

    def insert_message(self, sender_id, receiver_id, message, status):
        self.cursor.execute('INSERT INTO messages ("user_sender_id", "user_receiver_id", "message", "status") '
                            'VALUES (?, ?, ?, ?)',
                            (sender_id, receiver_id, message, status))
        self.conn.commit()

    def get_user_messages(self, receiver_id):
        result = self.cursor.execute('SELECT message FROM messages WHERE user_receiver_id = ?',
                                     (receiver_id,))
        return result.fetchall()

    def insert_or_update_user_address(self, user_id, user_address):
        result = self.cursor.execute('SELECT user_url FROM user_address '
                                     'WHERE user_id = ? and user_url = ? and status = "Active"',
                                     (user_id, user_address))
        if result.fetchall():
            return

        result = self.cursor.execute('SELECT user_url FROM user_address '
                                     'WHERE user_id = ? and user_url = ? and status = "Not available"',
                                     (user_id, user_address))

        if result.fetchall():
            self.cursor.execute('UPDATE user_address SET status = "Active"'
                                'WHERE user_id = ? and user_url = ?',
                                (user_id, user_address))
        else:
            self.cursor.execute('INSERT INTO user_address ("user_id", "user_url") '
                                'VALUES (?, ?)',
                                (user_id, user_address))
        self.conn.commit()

    def __del__(self):
        self.cursor.close()
        self.conn.close()


class DatabaseHandler:

    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, 'database.sqlite')

        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def create_users_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            phone TEXT NOT NULL)
            ''')

    def create_messages_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_sender_id INTEGER NOT NULL,
            user_receiver_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL,
            receive_date DATETIME DEFAULT CURRENT_TIMESTAMP)
            ''')

    def create_user_address_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_address
            (id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            user_url TEXT NOT NULL,
            status TEXT DEFAULT "Active",
            last_used DATETIME DEFAULT CURRENT_TIMESTAMP)
            ''')

    def insert_user(self, username, phone_number):
        if self.is_user_exists(username=username):
            return

        if self.is_phone_exists(phone_number):
            return

        self.cursor.execute('INSERT INTO users ("username", "phone") VALUES (?, ?)',
                            (username, phone_number))
        self.conn.commit()

    def insert_message(self, sender_id, receiver_id, message, status):
        if not self.is_user_exists(user_id=sender_id):
            return

        if not self.is_user_exists(user_id=receiver_id):
            return

        self.cursor.execute('INSERT INTO messages ("user_sender_id", "user_receiver_id", "message", "status") '
                            'VALUES (?, ?, ?, ?)',
                            (sender_id, receiver_id, message, status))
        self.conn.commit()

    def insert_or_update_user_address(self, user_id, user_address):
        result = self.cursor.execute('SELECT user_url FROM user_address '
                                     'WHERE user_id = ? and user_url = ? and status = "Active"',
                                     (user_id, user_address))
        if result.fetchall():
            return

        result = self.cursor.execute('SELECT user_url FROM user_address '
                                     'WHERE user_id = ? and user_url = ? and status = "Not available"',
                                     (user_id, user_address))

        if result.fetchall():
            self.cursor.execute('UPDATE user_address SET status = "Active"'
                                'WHERE user_id = ? and user_url = ?',
                                (user_id, user_address))
        else:
            self.cursor.execute('INSERT INTO user_address ("user_id", "user_url") '
                                'VALUES (?, ?)',
                                (user_id, user_address))
        self.conn.commit()

    def deactivate_user_address(self, user_id, user_address):
        self.cursor.execute('UPDATE user_address SET status = "Not available"'
                            'WHERE user_id = ? and user_url = ?',
                            (user_id, user_address))
        self.conn.commit()

    def get_user_address(self, user_id):
        result = self.cursor.execute('SELECT user_url, status FROM user_address WHERE user_id = ?',
                                     (user_id,))
        return result.fetchall()

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


if __name__ == '__main__':
    # handler = DatabaseHandler()
    # handler.create_users_table()
    # handler.create_messages_table()
    # handler.create_user_address_table()
    #
    # # Add test users
    # handler.insert_user('user_1', '123456789')
    # handler.insert_user('user_2', '987654321')
    # handler.insert_or_update_user_address(1, 'http://127.0.0.1:6666')
    # handler.insert_or_update_user_address(2, 'http://127.0.0.1:7777')
    # handler.insert_message(1, 2, 'test', 'not sent')

    ram_handler = RAMDatabaseHandler()
    ram_handler.create_messages_table()
    ram_handler.create_user_address_table()

    ram_handler.insert_or_update_user_address(1, 'http://127.0.0.1:6666')
    ram_handler.insert_or_update_user_address(2, 'http://127.0.0.1:7777')

    ram_handler.insert_message(1, 2, 'test', 'not sent')
    ram_handler.insert_message(1, 2, 'test1', 'not sent')
    ram_handler.insert_message(1, 2, 'test2', 'not sent')

    messages = ram_handler.get_user_messages(2)
    print(messages)