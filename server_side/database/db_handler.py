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
        result = self.cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
        if result.fetchall():
            return

        result = self.cursor.execute('SELECT phone FROM users WHERE username = ?', (phone_number,))
        if result.fetchall():
            return

        self.cursor.execute('INSERT INTO users ("username", "phone") '
                            'VALUES (?, ?)', (username, phone_number))
        self.conn.commit()

    def insert_message(self, sender_id, receiver_id, message):
        result = self.cursor.execute('SELECT id FROM users WHERE id = ?', (sender_id,))
        if result.fetchall():
            return

        result = self.cursor.execute('SELECT id FROM users WHERE id = ?', (receiver_id,))
        if result.fetchall():
            return

        self.cursor.execute('INSERT INTO messages VALUES (?, ?, ?)', (sender_id, receiver_id, message))
        self.conn.commit()

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
