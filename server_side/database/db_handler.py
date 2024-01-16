import sqlite3


class DatabaseHandler:

    def __init__(self):
        self.conn = sqlite3.connect('database.sqlite')
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
            message TEXT NOT NULL)
            ''')

    def create_user_address_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_address
            (id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            known_address TEXT NOT NULL)
            ''')

    def insert_user(self, username, phone_number):
        if self.is_user_exists(username=username):
            return

        if self.is_phone_exists(phone_number):
            return

        self.cursor.execute('INSERT INTO users ("username", "phone") VALUES (?, ?)',
                            (username, phone_number))
        self.conn.commit()

    def insert_message(self, sender_id, receiver_id, message):
        if not self.is_user_exists(user_id=sender_id):
            return

        if not self.is_user_exists(user_id=receiver_id):
            return

        self.cursor.execute('INSERT INTO messages VALUES (?, ?, ?)', (sender_id, receiver_id, message))
        self.conn.commit()

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
    handler = DatabaseHandler()
    handler.create_users_table()
    handler.create_messages_table()
    handler.create_user_address_table()

    # Add test users
    handler.insert_user('user_1', '123456789')
    handler.insert_user('user_2', '987654321')
