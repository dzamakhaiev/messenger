import os
from scripts.get_container_info import get_container_host

INSIDE_DOCKER = int(os.environ.get('RUN_INSIDE_DOCKER', 0))
CI_RUN = int(os.environ.get('CI_RUN', 0))

CONTAINER_NAME = 'postgres'
CONTAINER_NAME = CONTAINER_NAME + '-ci' if CI_RUN else CONTAINER_NAME

DB_HOST = get_container_host(CONTAINER_NAME)
if DB_HOST is None:
    DB_HOST = DB_HOST + '-ci' if DB_HOST else DB_HOST
DB_PORT = 5432
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
