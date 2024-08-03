import sqlite3
from threading import Lock
from logger.logger import Logger

database_logger = Logger('sqlite')
global_lock = Lock()


class RAMDatabaseHandler:

    def __init__(self):
        try:
            database_logger.info('Connecting to SQLite.')
            self.conn = sqlite3.connect(':memory:', check_same_thread=False)
            self.cursor = self.conn.cursor()
            database_logger.info('SQLite in-memory connection opened.')
        except sqlite3.Error as e:
            quit(e)

    def cursor_with_lock(self, query, args):
        try:
            database_logger.debug(f'Execute query:\n{query}\nArgs:\n{args}')
            global_lock.acquire(True)
            result = self.cursor.execute(query, args)
            return result

        except sqlite3.DatabaseError as e:
            database_logger.debug(f'Query caused an error: {e}')
            self.conn.rollback()

        finally:
            global_lock.release()

    def cursor_with_commit(self, query, args=None, many=False):
        database_logger.debug(f'Execute query:\n{query}\nArgs:\n{args}')
        if args is None:
            args = []

        try:
            global_lock.acquire(True)
            if many:
                self.cursor.executemany(query, args)
            else:
                self.cursor.execute(query, args)
            self.conn.commit()

        except sqlite3.DatabaseError as e:
            database_logger.debug(f'Query caused an error: {e}')
            self.conn.rollback()

        finally:
            global_lock.release()

    def create_user_address_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_address
            (user_id INTEGER NOT NULL,
            user_address TEXT NOT NULL,
            PRIMARY KEY (user_id, user_address),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (user_address) REFERENCES address(user_address))
            ''')

    def create_usernames_table(self):
        self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS usernames
                    (user_id INTEGER UNIQUE,
                    username TEXT NOT NULL UNIQUE)
                    ''')

    def create_tokens_table(self):
        self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tokens
                    (user_id INTEGER UNIQUE,
                    token TEXT NOT NULL)
                    ''')

    def create_public_keys_table(self):
        self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS public_keys
                    (user_id INTEGER UNIQUE,
                    public_key TEXT NOT NULL,
                    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
                    ''')

    def create_all_tables(self):
        self.create_tokens_table()
        self.create_usernames_table()
        self.create_public_keys_table()
        self.create_user_address_table()

    def insert_user_address(self, user_id: int, user_address: str):
        self.cursor_with_commit(
            'INSERT OR IGNORE INTO user_address ("user_id", "user_address") VALUES (?, ?)',
            (user_id, user_address))

    def insert_username(self, user_id: int, username: str):
        self.cursor_with_commit(
            'INSERT OR IGNORE INTO usernames ("user_id", "username") VALUES (?, ?)',
            (user_id, username))

    def insert_user_token(self, user_id: int, token: str):
        self.cursor_with_commit(
            'INSERT OR IGNORE INTO tokens ("user_id", "token") VALUES (?, ?)',
            (user_id, token))

    def insert_user_public_key(self, user_id: int, public_key: str):
        self.cursor_with_commit(
            'INSERT OR IGNORE INTO public_keys ("user_id", "public_key") VALUES (?, ?)',
            (user_id, public_key))

    def get_user(self, user_id: int = None, username: str = None):
        if user_id:
            result = self.cursor_with_lock(
                'SELECT * FROM usernames WHERE user_id = ?', (user_id,))

        elif username:
            result = self.cursor_with_lock(
                'SELECT * FROM usernames WHERE username = ?', (username,))
        else:
            return

        result = result.fetchone()
        if result:
            return result

    def get_user_address(self, user_id: int):
        result = self.cursor_with_lock(
            'SELECT user_address FROM user_address WHERE user_id = ?',
            (user_id,))
        return [item[0] for item in result.fetchall()]  # convert tuple to string

    def get_username(self, user_id: int):
        result = self.cursor_with_lock(
            'SELECT username FROM usernames WHERE user_id = ?', (user_id,))
        result = result.fetchone()
        if result:
            return result[0]
        return ''

    def get_user_token(self, user_id: int):
        result = self.cursor_with_lock(
            'SELECT token FROM tokens WHERE user_id = ?', (user_id,))
        result = result.fetchone()
        if result:
            return result[0]

    def get_user_public_key(self, user_id: int):
        result = self.cursor_with_lock(
            'SELECT public_key FROM public_keys WHERE user_id = ?', (user_id,))
        result = result.fetchone()
        if result:
            return result[0]

    def get_user_id(self, username: str):
        result = self.cursor_with_lock(
            'SELECT user_id FROM usernames WHERE username = ?', (username,))
        result = result.fetchone()
        if result:
            return result[0]

    def delete_user(self, user_id: int = None, username: str = None):
        if user_id:
            self.cursor_with_commit(
                'DELETE FROM usernames WHERE user_id = ?', (user_id,))
        elif username:
            self.cursor_with_commit(
                'DELETE FROM usernames WHERE username = ?', (username,))

    def delete_user_address(self, user_id: int):
        self.cursor_with_commit(
            'DELETE FROM user_address WHERE user_id = ?', (user_id,))

    def delete_user_token(self, user_id: int):
        self.cursor_with_commit(
            'DELETE FROM tokens WHERE user_id = ?', (user_id,))

    def delete_user_public_key(self, user_id: int):
        self.cursor_with_commit(
            'DELETE FROM public_keys WHERE user_id = ?', (user_id,))

    def __del__(self):
        if self.conn and self.cursor:
            self.cursor.close()
            self.conn.close()
        database_logger.info('SQLite Connection closed.')


if __name__ == '__main__':
    ram_handler = RAMDatabaseHandler()
    ram_handler.create_user_address_table()

    ram_handler.insert_user_address(1, 'http://127.0.0.1:6666')
    ram_handler.insert_user_address(2, 'http://127.0.0.1:7777')
