import os
from logger.logger import Logger
from scripts.get_container_host import get_container_host

postgres_settings = Logger('postgres_settings')
postgres_settings.info('Start to read Postgres settings.')

INSIDE_DOCKER = int(os.environ.get('RUN_INSIDE_DOCKER', 0))
CI_RUN = int(os.environ.get('CI_RUN', 0))
postgres_settings.info(f'Run inside docker: {INSIDE_DOCKER}\n'
                       f'Continuous Integration: {CI_RUN}\n')

CONTAINER_NAME = 'postgres'
CONTAINER_NAME = CONTAINER_NAME + '-ci' if CI_RUN else CONTAINER_NAME
postgres_settings.info(f'Postgres container name: {CONTAINER_NAME}')

DB_HOST = get_container_host(CONTAINER_NAME)
DB_PORT = 5432
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
postgres_settings.info(f'Postgres host and port: {DB_HOST}:{DB_PORT}')
