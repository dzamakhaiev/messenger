"""
This is a handler for RabbitMQ instance in docker container.
"""
import json
import pika
from server_side.broker import settings
from logger.logger import Logger


broker_logger = Logger('broker')


class RabbitMQHandler:

    def __init__(self):
        try:
            broker_logger.info('Connect to RabbitMQ.')
            broker_logger.debug(f'RabbitMQ URL: {settings.CONNECT_URI}')
            self.parameters = pika.URLParameters(settings.CONNECT_URI)
            self.connection = pika.BlockingConnection(self.parameters)
            self.channel = self.connection.channel()
            broker_logger.info('RabbitMQ connection established.')

        except (pika.exceptions.AMQPConnectionError, AttributeError, Exception) as e:
            broker_logger.error(e)
            quit('Cannot connect to RabbitMQ.')

    def reconnect(self):
        try:
            broker_logger.info('Reconnect to RabbitMQ.')
            self.connection = pika.BlockingConnection(self.parameters)
            self.channel = self.connection.channel()
        except (pika.exceptions.AMQPConnectionError, AttributeError, Exception) as e:
            broker_logger.error(e)
            quit('Cannot connect to RabbitMQ.')

    def create_exchange(self, exchange_name='TestExchange'):
        broker_logger.info(f'Create an exchange: {exchange_name}.')
        return self.channel.exchange_declare(exchange_name, durable=True)

    def create_and_bind_queue(self, queue_name='TestQueue', exchange_name='TestExchange'):
        broker_logger.info(f'Create a queue: {queue_name} for {exchange_name}.')
        queue = self.channel.queue_declare(queue_name, durable=True)
        bind = self.channel.queue_bind(queue=queue_name, exchange=exchange_name)
        return queue, bind

    def send_message(self, exchange_name, queue_name, body: (str, dict)):
        """
        That recursive method tries to put message in queue.
        If it fails, method will reconnect and try it one more time.
        """

        broker_logger.info(f'Put message in queue {queue_name}.')
        if isinstance(body, dict):
            body = json.dumps(body)

        if self.channel.is_closed or self.connection.is_closed:
            self.reconnect()

        try:
            properties = pika.BasicProperties(content_type='text/plain',
                                              delivery_mode=settings.MQ_DELIVERY_MODE)
            self.channel.basic_publish(exchange=exchange_name, routing_key=queue_name,
                                       body=body, properties=properties)

        except (pika.exceptions.StreamLostError, ):
            self.reconnect()
            self.send_message(exchange_name, queue_name, body)

    def receive_message(self, queue_name):

        if self.get_queue_len(queue_name):
            broker_logger.info(f'Get message from queue {queue_name}.')
            method, _, body = self.channel.basic_get(queue_name)
            self.channel.basic_ack(method.delivery_tag)
            body = body.decode()
            return body

    def get_queue_len(self, queue_name):
        queue = self.channel.queue_declare(queue_name, passive=True)
        return queue.method.message_count

    def connect_and_consume_from_multiple_queues(self, queue_dict: dict):
        """
        That method creates constant connection to RabbitMQ instance and allows
        to receive messages from several queues from queue_dict.
        """
        broker_logger.info('Connect consumer to RabbitMQ.')

        def on_open(connection):
            connection.channel(on_open_callback=on_channel_open)

        def on_channel_open(channel):
            for q_name, func in queue_dict.items():
                channel.basic_consume(queue=q_name, on_message_callback=func)

        connection = pika.SelectConnection(self.parameters, on_open_callback=on_open)
        return connection


if __name__ == '__main__':
    handler = RabbitMQHandler()
    handler.create_exchange()
    handler.create_and_bind_queue()
    handler.send_message(queue_name='TestQueue', exchange_name='TestExchange', body={'Test': 'test'})
    print(handler.get_queue_len('TestQueue'))
    handler.receive_message('TestQueue')
    handler.receive_message('TestQueue')
