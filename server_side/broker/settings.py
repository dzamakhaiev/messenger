MQ_PORT = 5672
MQ_HOST = '192.168.50.100'
CONNECT_URI = f'amqp://guest:guest@{MQ_HOST}:{MQ_PORT}/%2F'
MQ_DELIVERY_MODE = 2  # Persistent mode saves messages on HDD in case of crash
