from unittest import TestCase
from pika import BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel
from server_side.broker.mq_handler import RabbitMQHandler
from server_side.app import settings
from tests import test_data


class TestUser(TestCase):

    def setUp(self):
        self.mq_handler = RabbitMQHandler()

    def test_reconnect(self):
        self.mq_handler.reconnect()
        self.assertTrue(isinstance(self.mq_handler.connection, BlockingConnection))
        self.assertTrue(isinstance(self.mq_handler.channel, BlockingChannel))

    def test_create_exchange(self):
        exchange_name = 'TestExchange'
        exchange_confirm = self.mq_handler.create_exchange(exchange_name=exchange_name)
        self.assertEqual('Exchange.DeclareOk', exchange_confirm.method.NAME)

    def test_create_and_bind_queue(self):
        exchange_name = 'TestExchange'
        self.mq_handler.create_exchange(exchange_name=exchange_name)

        queue_name = 'TestQueue'
        queue, bind = self.mq_handler.create_and_bind_queue(queue_name=queue_name,
                                                            exchange_name=exchange_name)

        self.assertEqual('Queue.DeclareOk', queue.method.NAME)
        self.assertEqual('Queue.BindOk', bind.method.NAME)
