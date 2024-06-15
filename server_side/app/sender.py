import os
import sys
import json
from threading import Thread

# Fix for run via cmd inside venv
current_file = os.path.realpath(__file__)
current_dir = os.path.dirname(current_file)
repo_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, repo_dir)

from server_side.app import settings
from server_side.app.service import Service
from server_side.logger.logger import Logger
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
    sender_logger.info('Message received.')
    channel.basic_ack(delivery_tag=method.delivery_tag)
    message = body.decode()
    message = json.loads(message)

    address_list = message.get('address_list')
    msg_json = message.get('msg_json')
    sender_logger.debug(f'Message to send:\n{msg_json}To user address list:\n{address_list}')

    thread = Thread(target=service.send_message_by_list, args=(address_list, msg_json), daemon=True)
    sender_logger.debug(f'Thread "{thread.name}" created.')
    thread.start()
    sender_logger.debug(f'Thread "{thread.name}" started.')


def process_login(channel, method, properties, body):
    sender_logger.info('Login event received.')
    channel.basic_ack(delivery_tag=method.delivery_tag)
    login_msg = body.decode()
    login_msg = json.loads(login_msg)

    messages = service.get_messages(login_msg['user_id'])
    address_list = [login_msg['user_address']]
    sender_logger.debug(f'Messages to send after log in:\n{messages}\nTo user address list:\n{address_list}')

    thread = Thread(target=service.send_messages_by_list, args=(address_list, messages), daemon=True)
    sender_logger.debug(f'Thread "{thread.name}" created.')
    thread.start()
    sender_logger.debug(f'Thread "{thread.name}" started.')


if __name__ == '__main__':
    try:
        msg_broker.create_exchange(settings.MQ_EXCHANGE_NAME)
        msg_broker.create_and_bind_queue(settings.MQ_MSG_QUEUE_NAME, settings.MQ_EXCHANGE_NAME)
        msg_broker.create_and_bind_queue(settings.MQ_LOGIN_QUEUE_NAME, settings.MQ_EXCHANGE_NAME)

        sender_logger.info('Sender logger started.')
        queue_dict = {settings.MQ_MSG_QUEUE_NAME: process_message, settings.MQ_LOGIN_QUEUE_NAME: process_login}
        connection = msg_broker.connect_and_consume_from_multiple_queues(queue_dict)
        connection.ioloop.start()

    except (KeyboardInterrupt, Exception) as e:
        sender_logger.info('Sender logger ended.')
        quit(e)

