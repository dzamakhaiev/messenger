"""
Main entry point for python REST API application.
That module processes client's requests using Flask framework.
"""

import os
import sys
import jwt
from functools import wraps
from datetime import datetime, timedelta
from pydantic import ValidationError
from flask import Flask, request, jsonify

# Fix for run via cmd inside venv
current_file = os.path.realpath(__file__)
current_dir = os.path.dirname(current_file)
repo_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, repo_dir)

from server_side.app import routes  # pylint: disable=import-error
from server_side.app import settings
from server_side.app.service import Service
from server_side.logger.logger import Logger
from server_side.broker.mq_handler import RabbitMQHandler
from server_side.app.models import UserLogin, User, Message
from server_side.database.postgres_handler import PostgresHandler
from server_side.database.sqlite_handler import RAMDatabaseHandler


# Set up listener and its logger
app = Flask(__name__)
app.config['SECRET_KEY'] = 'replace_that_secret_key'  # do not use it on production
listener_logger = Logger('listener')

# To avoid initializing db connections while importing functions for unit tests
hdd_db_handler = None
ram_db_handler = None
mq_handler = None
service = None


def initialize_database_connections(hdd_db_handler, ram_db_handler, mq_handler, service):
    # Set up DB handlers in separate function
    hdd_db_handler = PostgresHandler()
    ram_db_handler = RAMDatabaseHandler()
    mq_handler = RabbitMQHandler()
    service = Service(hdd_db_handler, ram_db_handler, mq_handler)

    hdd_db_handler.create_all_tables()
    ram_db_handler.create_all_tables()
    mq_handler.create_exchange(settings.MQ_EXCHANGE_NAME)
    mq_handler.create_and_bind_queue(settings.MQ_MSG_QUEUE_NAME, settings.MQ_EXCHANGE_NAME)
    mq_handler.create_and_bind_queue(settings.MQ_LOGIN_QUEUE_NAME, settings.MQ_EXCHANGE_NAME)

    return hdd_db_handler, ram_db_handler, mq_handler, service


def token_required(f):
    """
    Decorator for check_token function to wrap Flask protected endpoints.
    """
    @wraps(f)
    def decorated_func(*args, **kwargs):
        error_tuple = check_token()
        if error_tuple[0] is not None:
            return error_tuple

        return f(*args, **kwargs)
    return decorated_func


def check_token():
    """
    Check client's token for access to protected endpoints.
    :return: http error code and message or None if no error
    """
    listener_logger.info('Check authorization token.')
    auth_header = request.headers.get('Authorization')

    if auth_header:
        token = auth_header.split(' ')[-1]
    else:
        listener_logger.error('Authorization header not found.')
        return settings.NOT_AUTHORIZED, 401

    try:
        token_info = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        listener_logger.info('Token decoded.')

        listener_logger.info('Check token in database.')
        username = token_info.get('user')
        user_id = service.get_user_id_by_username(username)
        result = service.check_user_token(user_id=user_id, token=token)

        if not result:
            return settings.NOT_AUTHORIZED, 401
        return None, None  # To pass pylint check

    except jwt.exceptions.ExpiredSignatureError:
        listener_logger.error('Token expired.')
        return settings.INVALID_TOKEN, 401

    except jwt.exceptions.InvalidTokenError:
        listener_logger.error('Invalid token.')
        return settings.INVALID_TOKEN, 401


def create_token(username, user_id):
    """
    Create jwt token for client.
    :return: token
    """
    listener_logger.info('Create authorization token.')
    token = jwt.encode(
        {'user': username, 'exp': datetime.now() + timedelta(minutes=settings.TOKEN_EXP_MINUTES)},
        app.config['SECRET_KEY'], algorithm='HS256')

    service.store_user_token(user_id, token)
    listener_logger.debug('Token created.')
    return token


@app.route(f'{routes.USERS}', methods=['POST'])
def create_user():
    """
    Create new user.
    :return: user_id or http error
    """
    listener_logger.info('Create user.')
    try:
        user = User(**request.json)
    except ValidationError as e:
        listener_logger.error(f'User validation caused error: {e}')
        return settings.VALIDATION_ERROR, 400

    listener_logger.debug(f'Create user with username: {user.username}')
    username = hdd_db_handler.get_user(username=user.username)

    if username:
        listener_logger.error(f'Username "{username}" already exists.')
        return 'Username already exists.', 400

    user_id = service.create_user(user)
    listener_logger.info(f'User "{user.username}" created with id {user_id}')
    return jsonify({'user_id': user_id}), 201


@app.route(f'{routes.USERS}', methods=['GET'])
@token_required
def get_user():
    """
    Provide user information for authorized users.
    :return: user_id and public_key or http error
    """
    listener_logger.info('Get user.')
    if username := request.args.get('username'):
        user_id = service.get_user_id_by_username(username)
    else:
        listener_logger.error('Field "username" is missing.')
        return settings.VALIDATION_ERROR, 400

    if user_id:
        listener_logger.debug(f'User found: {user_id}')
        public_key = service.get_user_public_key(user_id)
        return jsonify({'user_id': user_id, 'public_key': public_key})

    listener_logger.error(f'User "{username}" not found.')
    return f'User "{username}" not found.', 404


@app.route(f'{routes.USERS}', methods=['DELETE'])
def delete_user():
    """
    Delete user by user_id without any checks (for now).
    :return: confirmation message or http error
    """
    listener_logger.info('Delete user.')

    if user_id := request.json.get('user_id'):
        service.delete_user(user_id)
        listener_logger.debug(f'User deleted: {user_id}')
        return 'User deleted.', 200

    listener_logger.error('Field "user_id" is missing.')
    return settings.VALIDATION_ERROR, 400


@app.route(routes.LOGIN, methods=['POST'])
def login():
    """
    Complex function that:
    - check user credentials
    - create token for client if client has no token
    - cache frequently used data: username, user_id, token, public_key
    - send event to check not sent messages for current user_id and send one more time

    :return: user_id and token or http error
    """
    listener_logger.info('Login request.')
    listener_logger.debug(f'Request: {request.json}')

    try:
        user = UserLogin(**request.json)
    except ValidationError as e:
        listener_logger.error(f'Login validation caused error: {e}')
        return settings.VALIDATION_ERROR, 400

    password_correct = service.check_password(user.username, user.password)
    if password_correct:
        listener_logger.debug(f'Login successful for username: {user.username}')

        user_id = service.get_user_id_by_username(user.username)
        ram_db_handler.insert_username(user_id, user.username)

        token = service.get_user_token(user_id)
        if token is None:
            token = create_token(user.username, user_id)
            service.store_user_token(user_id, token)

        service.store_user_address(user_id, user.user_address)
        service.store_user_public_key(user_id, user.public_key)
        service.put_login_in_queue(user_id, user.user_address)

        listener_logger.debug(f'User id "{user_id}" logged in with token "{token}".')
        listener_logger.debug(f'User id "{user_id}" logged in with address "{user.user_address}".')
        return jsonify({'msg': 'Login successful.', 'user_id': user_id, 'token': token})

    listener_logger.error('Incorrect username or password.')
    return 'Incorrect username or password.', 401


@app.route(routes.LOGOUT, methods=['POST'])
@token_required
def logout():
    """
    Remove client's token from databases.
    :return: confirmation message and username or http error
    """
    listener_logger.info('Logout request.')
    listener_logger.debug(f'Request: {request.json}')

    if username := request.json.get('username'):
        listener_logger.info(f'Delete token for "{username}".')

        user_id = service.get_user_id_by_username(username)
        if not user_id:
            listener_logger.error(f'User "{username}" not found.')
            return settings.VALIDATION_ERROR, 400  # Hide real reason for other side

        service.delete_user_token(user_id)
        listener_logger.debug('Token deleted. User logged out.')
        return jsonify({'msg': 'Logout successful.', 'username': username})

    listener_logger.error('Field "username" is missing.')
    return settings.VALIDATION_ERROR, 400


@app.route(routes.MESSAGES, methods=['POST'])
@token_required
def process_messages():
    """
    Process message and put it into RabbitMQ queue to pass it to sender.py
    For authorized(with valid token) clients only.
    :return: confirmation message or http error
    """
    listener_logger.info('Messages request.')
    listener_logger.debug(f'Request: {request.json}')

    try:
        msg = Message(**request.json)
    except ValidationError as e:
        listener_logger.error(f'Message validation caused error: {e}')
        return settings.VALIDATION_ERROR, 400

    if not service.check_user_id(msg.receiver_id):
        listener_logger.error(f'User id "{msg.receiver_id}" not found.')
        return settings.VALIDATION_ERROR, 400

    username = service.get_username_by_user_id(msg.sender_id)
    listener_logger.debug(f'Username from message: "{msg.sender_username}"')
    listener_logger.debug(f'Username from database: "{username}"')

    if msg.sender_username == username:
        listener_logger.info(f'Send message to "{msg.receiver_id}" user id.')
        address_list = service.get_user_address(msg.receiver_id)
        service.put_message_in_queue(address_list, request.json)
        return 'Message processed.', 200

    listener_logger.error('Invalid username.')
    return settings.NOT_AUTHORIZED, 401


@app.route(routes.HEALTH, methods=['HEAD'])
def health_check():
    """
    Simple health check for listener service.
    :return: http OK status
    """
    listener_logger.info('Health checked for other services.')
    return 'OK', 200


if __name__ == '__main__':
    listener_logger.info('Listener started.')

    try:
        # To import functions for unit tests without initializing databases connections
        global hdd_db_handler, ram_db_handler, mq_handler, service
        hdd_db_handler, ram_db_handler, mq_handler, service = initialize_database_connections(
            hdd_db_handler, ram_db_handler, mq_handler, service)

        app.run(host=settings.REST_API_HOST, port=settings.REST_API_PORT, debug=True)
    except Exception as e:
        listener_logger.info(f'Listener failed with unexpected error:\n{e}.')

    listener_logger.info('Listener ended.')
