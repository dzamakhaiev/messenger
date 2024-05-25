import os
import sys
import json
import logging
from time import sleep
from threading import Thread, Event

# Fix for run via cmd inside venv
current_file = os.path.realpath(__file__)
current_dir = os.path.dirname(current_file)
repo_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, repo_dir)

from server_side.app import settings
from server_side.app.service import Service
from server_side.broker.mq_handler import RabbitMQHandler
from server_side.database.db_handler import RAMDatabaseHandler

sender_logger = logging.getLogger(__name__)
sender_logger.setLevel(logging.INFO)

formatter = logging.Formatter(settings.LOG_FORMAT)
handler = logging.FileHandler(f"../logs/sender.log")
handler.setFormatter(formatter)
sender_logger.addHandler(handler)


msg_broker = RabbitMQHandler()
ram_db_handler = RAMDatabaseHandler()
ram_db_handler.create_messages_table()
ram_db_handler.create_user_address_table()
service = Service(None, ram_db_handler, msg_broker)


class Sender:

    def run_sender(self):
        sender_logger.info('Sender logger started.')

        while True:

            try:
                message = msg_broker.receive_message(settings.MQ_MSG_QUEUE_NAME)
                if message:

                    message = json.loads(message)
                    address_list = message.get('address_list')
                    msg_json = message.get('msg_json')

                    print(address_list)
                    print(msg_json)
                    service.send_message_by_list(address_list, msg_json)

            except KeyboardInterrupt:
                sender_logger.info('Sender logger ended.')
                break

            except Exception as e:
                sender_logger.error(e)
                print(e)

            sleep(0.1)


if __name__ == '__main__':
    sender = Sender()
    sender.run_sender()
