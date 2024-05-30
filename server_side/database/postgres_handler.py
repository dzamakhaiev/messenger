import psycopg2
from server_side.database import settings
from server_side.logger.logger import get_logger

database_logger = get_logger('postgres_database')


class PostgresHandler:

    def __init__(self):
        try:
            database_logger.info('PostgreSQL connection opened.')
            self.connection = psycopg2.connect(database=settings.DB_NAME, user=settings.DB_USER, port=settings.DB_PORT,
                                               password=settings.DB_PASSWORD, host=settings.DB_HOST)
            self.cursor = self.connection.cursor()
        except (psycopg2.DatabaseError, Exception) as e:
            database_logger.error(e)
            quit()

    def cursor_execute(self, query, args=None):
        if args is None:
            args = []

        database_logger.debug(f'Execute query:\n{query}\nArgs:\n{args}')
        self.cursor.execute(query, args)
        return self.cursor

    def cursor_with_commit(self, query, args=None, many=False):
        if args is None:
            args = []

        try:
            database_logger.debug(f'Execute query:\n{query}\nArgs:\n{args}')
            if many:
                self.cursor.executemany(query, args)
            else:
                self.cursor.execute(query, args)
            self.connection.commit()

        except (psycopg2.OperationalError, psycopg2.errors.UniqueViolation):
            self.connection.rollback()

    def create_users_table(self):
        self.cursor_with_commit('''
            CREATE TABLE IF NOT EXISTS users
            (id SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL)
            ''')

    def create_messages_table(self):
        self.cursor_with_commit('''
            CREATE TABLE IF NOT EXISTS messages
            (id SERIAL PRIMARY KEY,
            user_sender_id INTEGER NOT NULL,
            user_receiver_id INTEGER NOT NULL,
            sender_username TEXT NOT NULL,
            message TEXT NOT NULL,
            receive_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
            ''')

    def create_sessions_table(self):
        self.cursor_with_commit('''
            CREATE TABLE IF NOT EXISTS sessions
            (user_id INTEGER NOT NULL UNIQUE,
            session_id TEXT NOT NULL,
            expiration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
            ''')

    def create_user_address_table(self):
        self.cursor_with_commit('''
            CREATE TABLE IF NOT EXISTS user_address
            (user_id INTEGER NOT NULL,
            user_address TEXT NOT NULL,
            last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
            ''')

    def create_all_tables(self):
        database_logger.info('Create tables.')
        self.create_users_table()
        self.create_sessions_table()
        self.create_user_address_table()
        self.create_messages_table()

        database_logger.info('Create test users.')
        self.insert_user('user_1', '123456789')
        self.insert_user('user_2', '987654321')

    def get_user(self, user_id=None, username=None):
        if user_id:
            result = self.cursor_execute('SELECT id, username FROM users WHERE id = %s', (user_id,))
        elif username:
            result = self.cursor_execute('SELECT id, username FROM users WHERE username = %s', (username,))
        else:
            return

        result = result.fetchone()
        if result:
            return result

    def get_user_address(self, user_id):
        result = self.cursor_execute('SELECT user_address FROM user_address WHERE user_id = %s',
                                     (user_id,))
        return [item[0] for item in result.fetchall()]  # convert tuple to string

    def get_user_messages(self, receiver_id):
        result = self.cursor_execute('SELECT * FROM messages WHERE user_receiver_id = %s',
                                     (receiver_id,))
        return result.fetchall()

    def get_user_password(self, username):
        result = self.cursor_execute('SELECT password FROM users WHERE username = %s',
                                     (username,))
        result = result.fetchone()
        if result:
            return result[0]

    def get_username(self, user_id):
        result = self.cursor_execute('SELECT username FROM users WHERE id = %s', (user_id,))
        result = result.fetchone()
        if result:
            return result[0]
        else:
            return ''

    def get_user_id(self, username):
        result = self.cursor_execute('SELECT id FROM users WHERE username = %s', (username,))
        result = result.fetchone()
        if result:
            return result[0]
        else:
            return None

    def get_user_session(self, user_id):
        result = self.cursor_execute('SELECT session_id FROM sessions WHERE user_id = %s', (user_id,))
        result = result.fetchone()
        if result:
            return result[0]

    def get_session(self, session_id):
        result = self.cursor_execute('SELECT session_id FROM sessions WHERE session_id = %s', (session_id,))
        result = result.fetchone()
        if result:
            return result[0]

    def get_all_messages(self):
        result = self.cursor_execute('SELECT user_sender_id, user_receiver_id, '
                                     'sender_username, message, receive_date '
                                     'FROM messages;', ())
        return result.fetchall()

    def insert_user_address(self, user_id, user_address):
        self.cursor_with_commit('INSERT INTO user_address ("user_id", "user_address") VALUES (%s, %s)',
                                (user_id, user_address))

    def insert_user(self, username, phone_number, password='qwerty'):
        self.cursor_with_commit('INSERT INTO users ("username", "phone", "password") VALUES (%s, %s, %s)',
                                (username, phone_number, password))

    def insert_messages(self, messages):
        self.cursor_with_commit('INSERT INTO messages ('
                                '"user_sender_id", "user_receiver_id", "sender_username", "message", "receive_date") '
                                'VALUES (%s, %s, %s, %s, %s)', messages, many=True)

    def insert_session_id(self, user_id, session_id):
        self.cursor_with_commit('INSERT INTO sessions ("user_id", "session_id") VALUES (%s, %s)',
                                (user_id, session_id))

    def delete_all_messages(self):
        self.cursor_with_commit('DELETE FROM messages')

    def delete_user_messages(self, receiver_id):
        self.cursor_with_commit('DELETE FROM messages WHERE user_receiver_id = %s', (receiver_id,))

    def delete_user(self, user_id=None, username=None):
        if user_id:
            self.cursor_with_commit('DELETE FROM users WHERE id = %s', (user_id,))
        elif username:
            self.cursor_with_commit('DELETE FROM users WHERE username = %s', (username,))

    def __del__(self):
        self.cursor.close()
        self.connection.close()


if __name__ == '__main__':
    handler = PostgresHandler()
    handler.create_all_tables()
    handler.get_all_messages()