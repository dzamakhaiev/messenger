"""
This module contains class Srvice that provide logical layer
between listener, sender services and databases, broker handlers.
"""
import socket
import hashlib
import requests
from urllib.parse import urlparse

from server_side.app import settings
from logger.logger import Logger
from server_side.broker.mq_handler import RabbitMQHandler
from server_side.database.sqlite_handler import RAMDatabaseHandler
from server_side.database.postgres_handler import PostgresHandler


LOCAL_IP = socket.gethostbyname(socket.gethostname())
service_logger = Logger('service')


class Service:

    def __init__(self,
                 hdd_db_handler: PostgresHandler,
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
            url = url.replace(parsed_url.hostname, 'localhost')

        return url

    def send_message(self, url, msg_json):
        try:
            url = self.check_url(url)
            service_logger.info(f'Sent message to url: {url}')
            response = requests.post(url, json=msg_json, timeout=5)
            service_logger.debug(f'Message sent with status code: {response.status_code}')
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

            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
                service_logger.error(e)

        if not message_received:
            service_logger.info('Message not sent. Store it into DB.')
            self.store_message_to_db(msg_json)
        return message_received

    def send_messages_by_list(self, address_list, messages):
        service_logger.info('Send messages by address list.')
        messages_to_delete = []

        for message in messages:
            msg_id, sender_id, receiver_id, sender_username, msg, msg_date = message
            msg_json = {'message': msg, 'sender_id': sender_id, 'sender_username': sender_username,
                        'receiver_id': receiver_id, 'send_date': msg_date.strftime(settings.DATETIME_FORMAT)}
            msg_received = self.send_message_by_list(address_list, msg_json)

            if msg_received:
                messages_to_delete.append(msg_id)

        messages_to_delete = ','.join([str(msg) for msg in messages_to_delete])
        if messages_to_delete:
            self.hdd_db_handler.delete_messages(messages_to_delete)
            service_logger.info('Message deleted from DB.')

    def create_user(self, user):
        service_logger.info('Create new user.')
        password = hashlib.sha256(str(user.password).encode()).hexdigest()
        self.hdd_db_handler.insert_user(user.username, user.phone_number, password)
        user_id = self.hdd_db_handler.get_user_id(user.username)

        self.ram_db_handler.insert_username(user_id, user.username)
        service_logger.info(f'User with {user.username} created: user id "{user_id}".')
        return user_id

    def store_message_to_db(self, msg_json):
        service_logger.debug(f'Message stored in HDD DB:\n{msg_json}')
        self.hdd_db_handler.insert_message(msg_json.get('sender_id'),
                                           msg_json.get('receiver_id'),
                                           msg_json.get('sender_username'),
                                           msg_json.get('message'))

    def store_user_address(self, user_id, user_address):
        service_logger.info('Store user user addresses in HDD and RAM DBs.')
        self.hdd_db_handler.insert_address(user_address)
        self.ram_db_handler.insert_user_address(user_id, user_address)
        self.hdd_db_handler.insert_user_address(user_id, user_address)

    def store_user_token(self, user_id, token):
        service_logger.info('Store user token.')
        service_logger.debug(token)
        self.hdd_db_handler.insert_user_token(user_id, token)
        self.ram_db_handler.insert_user_token(user_id, token)

    def store_user_public_key(self, user_id, public_key):
        service_logger.info('Store user public key.')
        service_logger.debug(public_key)
        self.hdd_db_handler.insert_user_public_key(user_id, public_key)
        self.ram_db_handler.insert_user_public_key(user_id, public_key)

    def put_message_in_queue(self, address_list, msg_json):
        service_logger.info(f'Put message in {settings.MQ_MSG_QUEUE_NAME} queue.')
        queue_json = {'address_list': address_list, 'msg_json': msg_json}
        self.mq_handler.send_message(exchange_name=settings.MQ_EXCHANGE_NAME,
                                     queue_name=settings.MQ_MSG_QUEUE_NAME,
                                     body=queue_json)

    def put_login_in_queue(self, user_id, user_address):
        service_logger.info(f'Put message in {settings.MQ_LOGIN_QUEUE_NAME} queue.')
        queue_json = {'user_id': user_id, 'user_address': user_address}
        self.mq_handler.send_message(exchange_name=settings.MQ_EXCHANGE_NAME,
                                     queue_name=settings.MQ_LOGIN_QUEUE_NAME,
                                     body=queue_json)

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

        service_logger.debug(f'Address list: {address_list}')
        return address_list

    def get_user_token(self, user_id):
        service_logger.info(f'Get user token for user id "{user_id}".')
        token = self.ram_db_handler.get_user_token(user_id)

        if not token:
            token = self.hdd_db_handler.get_user_token(user_id)

        service_logger.debug(f'User token: "{token}"')
        return token

    def get_user_public_key(self, user_id):
        service_logger.info(f'Get public key for user_id "{user_id}".')

        public_key = self.ram_db_handler.get_user_public_key(user_id)
        if public_key is None:
            public_key = self.hdd_db_handler.get_user_public_key(user_id)

        if public_key:
            service_logger.debug('User public key found.')
            self.ram_db_handler.insert_user_public_key(user_id, public_key)
            return public_key

        else:
            service_logger.error('User public key not found.')
            return None

    def get_messages(self, user_id):
        service_logger.info(f'Get messages for user id "{user_id}" from DB.')
        messages = self.hdd_db_handler.get_user_messages(user_id)
        service_logger.debug(f'Messages: {messages}')
        return messages

    def check_password(self, username, password: str):
        service_logger.info(f'Check "{username}" password.')
        exp_hashed_password = self.hdd_db_handler.get_user_password(username)

        if exp_hashed_password:
            service_logger.debug(f'"{username}" has password in database.')
            act_hashed_password = hashlib.sha256(password.encode()).hexdigest()
            return exp_hashed_password == act_hashed_password

        else:
            service_logger.error(f'"{username}" has no password in database.')
            return False

    def check_user_token(self, user_id, token):
        service_logger.info(f'Check user token for user_id "{user_id}".')
        exp_token = self.ram_db_handler.get_user_token(user_id)
        if exp_token is None:
            exp_token = self.hdd_db_handler.get_user_token(user_id)

        if token:
            service_logger.debug('User token found.')
            self.ram_db_handler.insert_user_token(user_id, token)
            return token == exp_token

        else:
            service_logger.error('User token not found.')
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
            self.delete_user_token(user_id)
            self.delete_user_public_key(user_id)

            self.hdd_db_handler.delete_user_messages(user_id)
            self.ram_db_handler.delete_user_address(user_id)
            self.hdd_db_handler.delete_user_address(user_id)
            self.ram_db_handler.delete_user(user_id=user_id)
            self.hdd_db_handler.delete_user(user_id=user_id)

            service_logger.info(f'User "{user_id}" deleted.')
            return True

        service_logger.error(f'User "{user_id}" not found.')
        return False

    def delete_user_token(self, user_id):
        service_logger.info(f'Check user token for user_id "{user_id}".')
        self.hdd_db_handler.delete_user_token(user_id)
        self.ram_db_handler.delete_user_token(user_id)

    def delete_user_public_key(self, user_id):
        service_logger.info(f'Check user public key for user_id "{user_id}".')
        self.hdd_db_handler.delete_user_public_key(user_id)
        self.ram_db_handler.delete_user_public_key(user_id)

    def __del__(self):
        service_logger.info('Service logger ended.')
