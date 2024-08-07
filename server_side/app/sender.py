"""
This module listens a RabbitMQ queues and send messages to defined ip address.
"""

import os
import sys
import json
from threading import Thread
from pika.exceptions import AMQPConnectionError

# Fix for run via cmd inside venv
current_file = os.path.realpath(__file__)
current_dir = os.path.dirname(current_file)
repo_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, repo_dir)

from server_side.app import settings
from server_side.app.service import Service
from logger.logger import Logger
from server_side.broker.mq_handler import RabbitMQHandler
from server_side.database.sqlite_handler import RAMDatabaseHandler
from server_side.database.postgres_handler import PostgresHandler

sender_logger = Logger('sender')

msg_broker = RabbitMQHandler()
ram_db_handler = RAMDatabaseHandler()
ram_db_handler.create_all_tables()
hdd_db_handler = PostgresHandler()
service = Service(hdd_db_handler, ram_db_handler, msg_broker)


def process_message(channel, method, properties, body):
    """
    This function process message from RabbitMQ queue and send message
    to ip address in separated thread.
    """
    sender_logger.info('Message received.')
    sender_logger.debug(f'Properties: "{properties}"')

    channel.basic_ack(delivery_tag=method.delivery_tag)
    message = body.decode()
    message = json.loads(message)

    address_list = message.get('address_list')
    msg_json = message.get('msg_json')
    sender_logger.debug(f'Message to send:\n{msg_json}To user address list:\n{address_list}')

    thread = Thread(target=service.send_message_by_list,
                    args=(address_list, msg_json), daemon=True)
    sender_logger.debug(f'Thread "{thread.name}" created.')
    thread.start()
    sender_logger.debug(f'Thread "{thread.name}" started.')


def process_login(channel, method, properties, body):
    """
    This function process message from RabbitMQ queue and check all not send messages
    for defined user and try it send one more time after user logged in.
    """
    sender_logger.info('Login event received.')
    sender_logger.debug(f'Properties: "{properties}"')

    channel.basic_ack(delivery_tag=method.delivery_tag)
    login_msg = body.decode()
    login_msg = json.loads(login_msg)
    sender_logger.debug(f'Login message: {login_msg}')

    messages = service.get_messages(login_msg['user_id'])
    address_list = [login_msg['user_address']]
    sender_logger.debug(f'Messages to send after log in:\n{messages}\n'
                        f'To user address list:\n{address_list}')

    thread = Thread(target=service.send_messages_by_list,
                    args=(address_list, messages), daemon=True)
    sender_logger.debug(f'Thread "{thread.name}" created.')
    thread.start()
    sender_logger.debug(f'Thread "{thread.name}" started.')


if __name__ == '__main__':
    msg_broker.create_exchange(settings.MQ_EXCHANGE_NAME)
    msg_broker.create_and_bind_queue(settings.MQ_MSG_QUEUE_NAME, settings.MQ_EXCHANGE_NAME)
    msg_broker.create_and_bind_queue(settings.MQ_LOGIN_QUEUE_NAME, settings.MQ_EXCHANGE_NAME)

    while True:

        try:
            sender_logger.info('Sender logger started.')
            queue_dict = {settings.MQ_MSG_QUEUE_NAME: process_message,
                          settings.MQ_LOGIN_QUEUE_NAME: process_login}
            connection = msg_broker.connect_and_consume_from_multiple_queues(queue_dict)
            connection.ioloop.start()

        except AMQPConnectionError as e:
            sender_logger.error(f'Connection to RabbitMQ lost: {e}')

        except KeyboardInterrupt:
            sender_logger.info('Sender logger ended.')
            connection.close()
            connection.ioloop.stop()
            sys.exit(0)

        except Exception as e:
            sender_logger.error(e)
            connection.close()
            connection.ioloop.stop()
            sys.exit(1)

