from time import sleep
from unittest import TestCase
from pika import BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel
from server_side.broker.mq_handler import RabbitMQHandler


WAIT_MESSAGE_TIME = 0.3


class TestUser(TestCase):

    def setUp(self):
        self.mq_handler = RabbitMQHandler()
        self.exchange_name = 'TestExchange'
        self.queue_name = 'TestQueue'

    def test_reconnect(self):
        self.mq_handler.reconnect()
        self.assertTrue(isinstance(self.mq_handler.connection, BlockingConnection))
        self.assertTrue(isinstance(self.mq_handler.channel, BlockingChannel))

    def test_create_exchange(self):
        exchange_confirm = self.mq_handler.create_exchange(exchange_name=self.exchange_name)
        self.assertEqual('Exchange.DeclareOk', exchange_confirm.method.NAME)

    def test_create_and_bind_queue(self):
        self.mq_handler.create_exchange(exchange_name=self.exchange_name)
        queue, bind = self.mq_handler.create_and_bind_queue(queue_name=self.queue_name,
                                                            exchange_name=self.exchange_name)

        self.assertEqual('Queue.DeclareOk', queue.method.NAME)
        self.assertEqual('Queue.BindOk', bind.method.NAME)

    def test_send_message(self):
        # Preconditions: test exchange and test queue
        self.mq_handler.create_exchange(exchange_name=self.exchange_name)
        self.mq_handler.create_and_bind_queue(queue_name=self.queue_name,
                                              exchange_name=self.exchange_name)

        # Put message to queue
        message = 'test'
        self.mq_handler.send_message(
            exchange_name=self.exchange_name, queue_name=self.queue_name, body=message)

        # Get message from queue
        _, _, body = self.mq_handler.channel.basic_get(queue=self.queue_name, auto_ack=True)
        self.assertEqual(message, body.decode())

    def test_receive_message(self):
        # Preconditions: test exchange and test queue
        self.mq_handler.create_exchange(exchange_name=self.exchange_name)
        self.mq_handler.create_and_bind_queue(queue_name=self.queue_name,
                                              exchange_name=self.exchange_name)

        # Put message to queue
        message = 'test'
        self.mq_handler.send_message(exchange_name=self.exchange_name, queue_name=self.queue_name,
                                     body=message)

        # Get message from queue
        sleep(WAIT_MESSAGE_TIME)
        body = self.mq_handler.receive_message(queue_name=self.queue_name)
        self.assertEqual(message, body)

    def test_get_queue_len(self):
        # Preconditions: test exchange and test queue
        self.mq_handler.create_exchange(exchange_name=self.exchange_name)
        self.mq_handler.create_and_bind_queue(queue_name=self.queue_name,
                                              exchange_name=self.exchange_name)

        # Put message to queue
        message = 'test'
        self.mq_handler.send_message(exchange_name=self.exchange_name, queue_name=self.queue_name,
                                     body=message)

        # Check queue len
        sleep(WAIT_MESSAGE_TIME)
        queue_len = self.mq_handler.get_queue_len(queue_name=self.queue_name)
        self.assertEqual(queue_len, 1)

    def tearDown(self):
        self.mq_handler.channel.queue_delete(queue=self.queue_name)
        self.mq_handler.channel.exchange_delete(exchange=self.exchange_name)
