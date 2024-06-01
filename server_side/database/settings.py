import os

INSIDE_DOCKER = int(os.environ.get('RUN_INSIDE_DOCKER', 0))
DB_HOST = 'postgres' if INSIDE_DOCKER else 'localhost'
DB_PORT = 5432
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'

REDIS_HOST = 'redis' if INSIDE_DOCKER else 'localhost'
REDIS_PORT = '6379'
