import os

INSIDE_DOCKER = int(os.environ.get('RUN_INSIDE_DOCKER', 0))
CI_RUN = int(os.environ.get('CI_RUN', 0))

MQ_PORT = 5672
MQ_HOST = 'rabbitmq' if INSIDE_DOCKER else 'localhost'
DB_HOST = MQ_HOST + '-ci' if CI_RUN else MQ_HOST
CONNECT_URI = f'amqp://guest:guest@{MQ_HOST}:{MQ_PORT}/%2F'
MQ_DELIVERY_MODE = 2  # Persistent mode saves messages on HDD in case of crash
