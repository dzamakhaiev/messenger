import sqlite3


class DatabaseHandler:

    def __init__(self):
        self.conn = sqlite3.connect('database.sqlite')
        self.cursor = self.conn.cursor()

    def create_user_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users
            (id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            phone TEXT NOT NULL)
            ''')

    def create_messages_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages
            (id INTEGER PRIMARY KEY,
            user_sender_id INTEGER NOT NULL,
            user_sender_id INTEGER NOT NULL,
            message TEXT NOT NULL)
            ''')

    def create_user_address_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_address
            (id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            known_address TEXT NOT NULL)
            ''')

    def __del__(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    handler = DatabaseHandler()
    handler.create_user_table()
    handler.create_messages_table()
    handler.create_user_address_table()
