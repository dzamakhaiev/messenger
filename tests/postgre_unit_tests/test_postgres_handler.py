import os
from unittest import TestCase, skipIf
import psycopg2
from docker import from_env
from docker.errors import DockerException
from server_side.database.postgres_handler import PostgresHandler
from logger.logger import Logger


postgres_test_logger = Logger('postgres_test_logger')


try:
    # Check docker is running
    docker = from_env()
    docker_running = True
    postgres_running = False

    # Check Postgres container is running
    containers = docker.containers.list()
    containers = [container.name for container in containers]
    if 'postgres' in containers or 'postgres-ci' in containers:
        postgres_running = True

except DockerException as e:
    docker_running = False
    postgres_running = False


RUN_INSIDE_DOCKER = int(os.environ.get('RUN_INSIDE_DOCKER', 0))
CI_RUN = int(os.environ.get('CI_RUN', 0))
CONDITION = not (docker_running and postgres_running)
REASON = 'Docker/postgres container is not running'
WAIT_MESSAGE_TIME = 0.3

postgres_test_logger.info(f'Postgres unit tests.\n'
                          f'Run inside docker: {RUN_INSIDE_DOCKER}\n'
                          f'Continuous Integration: {CI_RUN}\n'
                          f'Condition for skip tests: {CONDITION}')


class TestPostgres(TestCase):

    @classmethod
    def setUpClass(cls):

        if RUN_INSIDE_DOCKER and CI_RUN:
            client = docker.from_env()
            container = client.containers.get('postgres-ci')
            container_info = container.attrs

            networks = container_info.get('NetworkSettings').get('Networks')
            bridge_network = networks.get('bridge')
            ip_address = bridge_network.get('IPAddress')
            cls.postgres_host = ip_address

        else:
            cls.postgres_host = 'localhost'

        postgres_test_logger.info(f'Container Postgres runs on IP {cls.postgres_host}')

    def setUp(self):
        self.hdd_db_handler = PostgresHandler(host=self.postgres_host)

    @skipIf(CONDITION, REASON)
    def test_create_users_table(self):
        self.hdd_db_handler.create_users_table()

        query = 'SELECT EXISTS(SELECT relname FROM pg_class WHERE relname = %s)'
        result = self.hdd_db_handler.cursor_execute(query, ('users',))
        result = result.fetchone()
        self.assertTrue(result[0])

    @skipIf(CONDITION, REASON)
    def test_create_messages_table(self):
        self.hdd_db_handler.create_messages_table()

        query = 'SELECT EXISTS(SELECT relname FROM pg_class WHERE relname = %s)'
        result = self.hdd_db_handler.cursor_execute(query, ('messages',))
        result = result.fetchone()
        self.assertTrue(result[0])

    @skipIf(CONDITION, REASON)
    def test_create_address_table(self):
        self.hdd_db_handler.create_address_table()

        query = 'SELECT EXISTS(SELECT relname FROM pg_class WHERE relname = %s)'
        result = self.hdd_db_handler.cursor_execute(query, ('address',))
        result = result.fetchone()
        self.assertTrue(result[0])

    @skipIf(CONDITION, REASON)
    def test_create_user_address_table(self):
        self.hdd_db_handler.create_user_address_table()

        query = 'SELECT EXISTS(SELECT relname FROM pg_class WHERE relname = %s)'
        result = self.hdd_db_handler.cursor_execute(query, ('user_address',))
        result = result.fetchone()
        self.assertTrue(result[0])

    @skipIf(CONDITION, REASON)
    def test_create_tokens_table(self):
        self.hdd_db_handler.create_tokens_table()

        query = 'SELECT EXISTS(SELECT relname FROM pg_class WHERE relname = %s)'
        result = self.hdd_db_handler.cursor_execute(query, ('tokens',))
        result = result.fetchone()
        self.assertTrue(result[0])

    @skipIf(CONDITION, REASON)
    def test_create_public_keys_table(self):
        self.hdd_db_handler.create_public_keys_table()

        query = 'SELECT EXISTS(SELECT relname FROM pg_class WHERE relname = %s)'
        result = self.hdd_db_handler.cursor_execute(query, ('public_keys',))
        result = result.fetchone()
        self.assertTrue(result[0])

    @skipIf(CONDITION, REASON)
    def test_create_all_tables(self):
        self.hdd_db_handler.create_all_tables()
        all_tables = ['users', 'messages', 'address', 'user_address', 'tokens', 'public_keys']

        for table in all_tables:
            with self.subTest(f'Test "{table}" table exists.'):

                query = 'SELECT EXISTS(SELECT relname FROM pg_class WHERE relname = %s)'
                result = self.hdd_db_handler.cursor_execute(query, (table,))
                result = result.fetchone()
                self.assertTrue(result[0])

    def tearDown(self):
        # Drop all tables in HDD database
        query = "select 'drop table if exists "' || tablename || '" cascade;' from pg_tables;"
        self.hdd_db_handler.cursor_with_commit(query, [])
