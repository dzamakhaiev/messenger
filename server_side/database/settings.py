import os

INSIDE_DOCKER = int(os.environ.get('RUN_INSIDE_DOCKER', 0))
CI_RUN = int(os.environ.get('CI_RUN', 0))

CONTAINER_NAME = 'postgres'
DB_HOST = CONTAINER_NAME + '-ci' if CI_RUN else CONTAINER_NAME
DB_PORT = 5432
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
