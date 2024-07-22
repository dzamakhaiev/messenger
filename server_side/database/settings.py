import os

INSIDE_DOCKER = int(os.environ.get('RUN_INSIDE_DOCKER', 0))
CI_RUN = int(os.environ.get('CI_RUN', 0))

DB_HOST = 'postgres' if INSIDE_DOCKER else 'localhost'
DB_HOST = DB_HOST + '-ci' if CI_RUN else DB_HOST
DB_PORT = 5432
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
