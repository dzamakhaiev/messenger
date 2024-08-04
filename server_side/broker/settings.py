import os

INSIDE_DOCKER = int(os.environ.get('RUN_INSIDE_DOCKER', 0))
CI_RUN = int(os.environ.get('CI_RUN', 0))

CONTAINER_NAME = 'rabbitmq'
MQ_HOST = CONTAINER_NAME + '-ci' if CI_RUN else CONTAINER_NAME
MQ_PORT = 5672
CONNECT_URI = f'amqp://guest:guest@{MQ_HOST}:{MQ_PORT}/%2F'
MQ_DELIVERY_MODE = 2  # Persistent mode saves messages on HDD in case of crash
