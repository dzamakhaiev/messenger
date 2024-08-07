import os
import json
from time import sleep
from threading import Thread
from unittest import TestCase, skipIf
from pika import BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel
from scripts.get_container_info import docker_is_running, container_is_running
from server_side.broker.mq_handler import RabbitMQHandler
from logger.logger import Logger


rabbitmq_test_logger = Logger('rabbitmq_test_logger')
RUN_INSIDE_DOCKER = int(os.environ.get('RUN_INSIDE_DOCKER', 0))
CI_RUN = int(os.environ.get('CI_RUN', 0))
CONTAINER_NAME = 'rabbitmq-ci' if CI_RUN else 'rabbitmq'
DOCKER_RUNNING = docker_is_running()
CONTAINER_RUNNING = container_is_running(CONTAINER_NAME)
CONDITION = not (DOCKER_RUNNING and CONTAINER_RUNNING)
REASON = f'Docker/{CONTAINER_NAME} container is not running'
WAIT_MESSAGE_TIME = 0.3

rabbitmq_test_logger.info(f'RabbitMQ unit tests.\n'
                          f'Run inside docker: {RUN_INSIDE_DOCKER}\n'
                          f'Continuous Integration: {CI_RUN}\n'
                          f'Condition for skip tests: {CONDITION}')


class TestRabbitMQ(TestCase):

    def setUp(self):
        self.mq_handler = RabbitMQHandler()
        self.exchange_name = 'TestExchange'
        self.queue_name = 'TestQueue'

    @skipIf(CONDITION, REASON)
    def test_reconnect(self):
        self.mq_handler.reconnect()
        self.assertTrue(isinstance(self.mq_handler.connection, BlockingConnection))
        self.assertTrue(isinstance(self.mq_handler.channel, BlockingChannel))

    @skipIf(CONDITION, REASON)
    def test_create_exchange(self):
        exchange_confirm = self.mq_handler.create_exchange(exchange_name=self.exchange_name)
        self.assertEqual('Exchange.DeclareOk', exchange_confirm.method.NAME)

    @skipIf(CONDITION, REASON)
    def test_create_and_bind_queue(self):
        self.mq_handler.create_exchange(exchange_name=self.exchange_name)
        queue, bind = self.mq_handler.create_and_bind_queue(queue_name=self.queue_name,
                                                            exchange_name=self.exchange_name)

        self.assertEqual('Queue.DeclareOk', queue.method.NAME)
        self.assertEqual('Queue.BindOk', bind.method.NAME)

    @skipIf(CONDITION, REASON)
    def test_send_message(self):
        # Preconditions: test exchange and test queue
        self.mq_handler.create_exchange(exchange_name=self.exchange_name)
        self.mq_handler.create_and_bind_queue(queue_name=self.queue_name,
                                              exchange_name=self.exchange_name)

        # First case: put string message to queue
        message = 'test'
        self.mq_handler.send_message(
            exchange_name=self.exchange_name, queue_name=self.queue_name, body=message)
        _, _, body = self.mq_handler.channel.basic_get(queue=self.queue_name, auto_ack=True)
        self.assertEqual(message, body.decode())

        # Second case: put dict message to queue
        message = {'message': 'test'}
        self.mq_handler.send_message(
            exchange_name=self.exchange_name, queue_name=self.queue_name, body=message)
        _, _, body = self.mq_handler.channel.basic_get(queue=self.queue_name, auto_ack=True)
        self.assertEqual(message, json.loads(body.decode()))

    @skipIf(CONDITION, REASON)
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

    @skipIf(CONDITION, REASON)
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

    @skipIf(CONDITION, REASON)
    def test_connect_and_consume_from_multiple_queues(self):
        # Preconditions
        self.mq_handler.create_exchange(exchange_name=self.exchange_name)
        self.mq_handler.create_and_bind_queue(queue_name=self.queue_name,
                                              exchange_name=self.exchange_name)
        external_results = {}

        def run_io_loop_in_thread():
            def process_message_callback(channel, method, properties, body):
                # Create callback function to process messages
                channel.basic_ack(delivery_tag=method.delivery_tag)
                message = body.decode()
                message = json.loads(message)
                external_results['message'] = message

            # Run io loop for defined queue with callback function
            queue_dict = {self.queue_name: process_message_callback}
            connection = self.mq_handler.connect_and_consume_from_multiple_queues(queue_dict)
            connection.ioloop.start()

        # Run infinite loop in daemon thread
        thread = Thread(target=run_io_loop_in_thread, daemon=True)
        thread.start()

        # Send message
        message = {'message': 'test message for consumer'}
        self.mq_handler.send_message(exchange_name=self.exchange_name, queue_name=self.queue_name,
                                     body=message)

        # Check message received
        sleep(WAIT_MESSAGE_TIME)
        self.assertEqual(len(external_results), 1)
        self.assertEqual(external_results.get('message'), message)

    def tearDown(self):
        self.mq_handler.channel.queue_delete(queue=self.queue_name)
        self.mq_handler.channel.exchange_delete(exchange=self.exchange_name)
