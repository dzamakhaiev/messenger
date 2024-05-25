import uuid
import socket
import requests
from urllib.parse import urlparse

from server_side.app import settings
from server_side.logger.logger import get_logger
from server_side.broker.mq_handler import RabbitMQHandler
from server_side.database.db_handler import HDDDatabaseHandler, RAMDatabaseHandler


LOCAL_IP = socket.gethostbyname(socket.gethostname())
service_logger = get_logger('service')


class Service:

    def __init__(self,
                 hdd_db_handler: HDDDatabaseHandler,
                 ram_db_handler: RAMDatabaseHandler,
                 mq_handler: RabbitMQHandler):

        service_logger.info('Service logger started.')
        self.hdd_db_handler = hdd_db_handler
        self.ram_db_handler = ram_db_handler
        self.mq_handler = mq_handler

    @staticmethod
    def check_url(url: str):
        parsed_url = urlparse(url)
        if parsed_url.hostname == LOCAL_IP:
            url.replace(parsed_url.hostname, 'localhost')

        return url

    def send_message(self, url, msg_json):
        try:
            url = self.check_url(url)
            service_logger.info(f'Sent message to url: {url}')
            response = requests.post(url, json=msg_json, timeout=5)
            service_logger.info(f'Message sent with status code: {response.status_code}')
            return response

        except requests.exceptions.ConnectionError as e:
            service_logger.error(f'Response with error: {e}')

    def send_message_by_list(self, address_list, msg_json):
        service_logger.info('Send message by address list.')
        message_received = False

        for user_address in address_list:
            try:
                response = self.send_message(user_address, msg_json)
                if response and response.status_code == 200:
                    message_received = True

            except Exception as e:  # debug only
                print(e)

        if not message_received:
            service_logger.info('Message not sent. Store it to DB in RAM.')
            self.store_message_to_ram_db(msg_json)
        return message_received

    def send_messages_by_list(self, address_list, messages):
        service_logger.info('Send messages by address list.')
        messages_to_delete = []

        for message in messages:
            msg_id, sender_id, receiver_id, sender_username, msg, msg_date = message
            msg_json = {'message': msg, 'sender_id': sender_id, 'sender_username': sender_username,
                        'receiver_id': receiver_id}
            msg_received = self.send_message_by_list(address_list, msg_json)

            if msg_received:
                service_logger.info('Message deleted from RAM DB.')
                messages_to_delete.append(msg_id)

        messages_to_delete = ','.join([str(msg) for msg in messages_to_delete])
        self.ram_db_handler.delete_messages(messages_to_delete)

    def create_user(self, user):
        service_logger.info('Create new user.')

        self.hdd_db_handler.insert_user(user.username, user.phone_number, user.password)
        user_id = self.hdd_db_handler.get_user_id(user.username)
        self.ram_db_handler.insert_username(user_id, user.username)

        service_logger.info(f'User with {user.username} created: user id "{user_id}".')
        return user_id

    def store_message_to_ram_db(self, msg_json):
        service_logger.debug(f'Message stored in RAM DB:\n{msg_json}')
        self.ram_db_handler.insert_message(msg_json.get('sender_id'),
                                           msg_json.get('receiver_id'),
                                           msg_json.get('sender_username'),
                                           msg_json.get('message'))

    def store_all_messages_to_hdd(self):
        messages = self.ram_db_handler.get_all_messages()
        if messages:
            self.hdd_db_handler.insert_messages(messages)

    def restore_all_messages_from_hdd(self):
        messages = self.hdd_db_handler.get_all_messages()
        if messages:
            self.ram_db_handler.insert_messages(messages)
            self.hdd_db_handler.delete_all_messages()

    def store_user_address_and_session(self, user_id, session_id, user_address):
        service_logger.info('Store user session and user addresses in HDD and RAM DBs.')
        self.ram_db_handler.insert_session_id(user_id, session_id)
        self.hdd_db_handler.insert_session_id(user_id, session_id)
        self.ram_db_handler.insert_user_address(user_id, user_address)
        self.hdd_db_handler.insert_user_address(user_id, user_address)

    def put_message_in_queue(self, address_list, msg_json):
        service_logger.info(f'Put message in {settings.MQ_MSG_QUEUE_NAME} queue.')
        queue_json = {'address_list': address_list, 'msg_json': msg_json}
        self.mq_handler.send_message(exchange_name=settings.MQ_EXCHANGE_NAME, queue_name=settings.MQ_MSG_QUEUE_NAME,
                                     body=queue_json)

    def put_login_in_queue(self, user_id, user_address):
        service_logger.info(f'Put message in {settings.MQ_LOGIN_QUEUE_NAME} queue.')
        queue_json = {'user_id': user_id, 'user_address': user_address}
        self.mq_handler.send_message(exchange_name=settings.MQ_EXCHANGE_NAME, queue_name=settings.MQ_LOGIN_QUEUE_NAME,
                                     body=queue_json)

    def get_or_create_user_session(self, user_id):
        service_logger.info(f'Get or create session for user id "{user_id}".')
        session_id = self.get_session_id(user_id)
        if not session_id:
            session_id = str(uuid.uuid4())

        service_logger.debug(f'Session id: "{session_id}".')
        return session_id

    def get_session_id(self, user_id):
        session_id = self.ram_db_handler.get_user_session(user_id)
        if session_id:
            return session_id
        else:
            return self.hdd_db_handler.get_user_session(user_id)

    def get_user_id_by_username(self, username):
        service_logger.debug(f'Get user id for username "{username}".')
        user_id = self.ram_db_handler.get_user_id(username)
        if not user_id:
            user_id = self.hdd_db_handler.get_user_id(username)

        return user_id

    def get_username_by_user_id(self, user_id):
        service_logger.debug(f'Get username for user id "{user_id}".')
        username = self.ram_db_handler.get_username(user_id)
        if not username:
            username = self.hdd_db_handler.get_username(user_id)

        if username:
            return username
        else:
            return ''

    def get_user_address(self, user_id):
        service_logger.info(f'Get user address for user id "{user_id}".')
        address_list = self.ram_db_handler.get_user_address(user_id)
        if not address_list:
            address_list = self.hdd_db_handler.get_user_address(user_id)

        return address_list

    def get_messages(self, user_id):
        service_logger.info(f'Get messages for user id "{user_id}".')
        messages = self.ram_db_handler.get_user_messages(user_id)
        self.ram_db_handler.delete_user_messages(user_id)

        service_logger.debug(messages)
        return messages

    def check_session_exists(self, session_id):
        service_logger.info(f'Check session id "{session_id}".')
        session_id = self.ram_db_handler.get_session(session_id)
        if not session_id:
            session_id = self.hdd_db_handler.get_session(session_id)

        if session_id:
            return True
        else:
            return False

    def check_user_id(self, user_id):
        service_logger.info(f'Check user id "{user_id}".')
        result = self.ram_db_handler.get_user(user_id=user_id)
        if not result:
            result = self.hdd_db_handler.get_user(user_id=user_id)

        if result:
            return True
        else:
            return False

    def delete_user(self, user_id):
        service_logger.info(f'Delete user id "{user_id}".')
        if self.check_user_id(user_id):
            self.ram_db_handler.delete_user(user_id=user_id)
            self.ram_db_handler.delete_user_messages(user_id)
            self.hdd_db_handler.delete_user(user_id=user_id)
            self.hdd_db_handler.delete_user_messages(user_id)

    def __del__(self):
        service_logger.info('Service logger ended.')
