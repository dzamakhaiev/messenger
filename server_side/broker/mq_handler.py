import json
import pika
from server_side.broker import settings
from server_side.logger.logger import get_logger


class RabbitMQHandler:

    def __init__(self):
        try:
            self.parameters = pika.URLParameters('amqp://guest:guest@localhost:5672/%2F')
            self.connection = pika.BlockingConnection(self.parameters)
            self.channel = self.connection.channel()
        except (pika.exceptions.AMQPConnectionError, AttributeError):
            quit('Cannot connect to RabbitMQ.')

    def reconnect(self):
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()

    def create_exchange(self, exchange_name='TestExchange'):
        self.channel.exchange_declare(exchange_name)

    def create_and_bind_queue(self, queue_name='TestQueue', exchange_name='TestExchange'):
        self.channel.queue_declare(queue_name, durable=True)
        self.channel.queue_bind(queue=queue_name, exchange=exchange_name)

    def send_message(self, exchange_name, queue_name, body):
        if isinstance(body, dict):
            body = json.dumps(body)

        properties = pika.BasicProperties(content_type='text/plain', delivery_mode=settings.MQ_DELIVERY_MODE)
        if self.channel.is_closed or self.connection.is_closed:
            self.reconnect()
        self.channel.basic_publish(exchange=exchange_name, routing_key=queue_name, body=body, properties=properties)

    def receive_message(self, queue_name):

        if self.get_queue_len(queue_name):
            method, _, body = self.channel.basic_get(queue_name)
            self.channel.basic_ack(method.delivery_tag)
            body = body.decode()
            return body

    def get_queue_len(self, queue_name):
        queue = self.channel.queue_declare(queue_name, passive=True)
        return queue.method.message_count

    def close_connection(self):
        if hasattr(self, 'connection') and self.connection.is_open:
            self.connection.close()

    def __del__(self):
        self.close_connection()


if __name__ == '__main__':
    handler = RabbitMQHandler()
    handler.create_exchange()
    handler.create_and_bind_queue()
    handler.send_message(queue_name='TestQueue', exchange_name='TestExchange', body={'Test': 'test'})
    print(handler.get_queue_len('TestQueue'))
    handler.receive_message('TestQueue')
    handler.receive_message('TestQueue')
    handler.close_connection()
