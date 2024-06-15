import os
import sys
import jwt
import routes
from datetime import datetime, timedelta
from pydantic import ValidationError
from flask import Flask, request, jsonify

# Fix for run via cmd inside venv
current_file = os.path.realpath(__file__)
current_dir = os.path.dirname(current_file)
repo_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, repo_dir)

from server_side.app import settings
from server_side.app.service import Service
from server_side.logger.logger import Logger
from server_side.broker.mq_handler import RabbitMQHandler
from server_side.app.models import UserLogin, User, Message
from server_side.database.sqlite_handler import RAMDatabaseHandler
from server_side.database.postgres_handler import PostgresHandler


# Set up listener and its logger
app = Flask(__name__)
app.config['SECRET_KEY'] = 'replace_that_secret_key'
listener_logger = Logger('listener')

# Set up DB handlers
hdd_db_handler = PostgresHandler()
ram_db_handler = RAMDatabaseHandler()
mq_handler = RabbitMQHandler()

hdd_db_handler.create_all_tables()
ram_db_handler.create_all_tables()
mq_handler.create_exchange(settings.MQ_EXCHANGE_NAME)
mq_handler.create_and_bind_queue(settings.MQ_MSG_QUEUE_NAME, settings.MQ_EXCHANGE_NAME)
mq_handler.create_and_bind_queue(settings.MQ_LOGIN_QUEUE_NAME, settings.MQ_EXCHANGE_NAME)

service = Service(hdd_db_handler, ram_db_handler, mq_handler)


def check_token(headers: dict):
    listener_logger.info('Check authorization token.')
    auth_header = headers.get('Authorization')

    if auth_header:
        token = auth_header.split(' ')[-1]
    else:
        listener_logger.error('Authorization header not found.')
        return settings.NOT_AUTHORIZED, 401

    try:
        jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        listener_logger.info('Token decoded.')

    except jwt.exceptions.ExpiredSignatureError:
        listener_logger.error('Token expired.')
        return settings.INVALID_TOKEN, 401

    except jwt.exceptions.InvalidTokenError:
        listener_logger.error('Invalid expired.')
        return settings.INVALID_TOKEN, 401


def create_token(username):
    listener_logger.info('Create authorization token.')
    token = jwt.encode({'user': username, 'exp': datetime.now() + timedelta(minutes=settings.TOKEN_EXP_MINUTES)},
                       app.config['SECRET_KEY'], algorithm='HS256')
    listener_logger.debug('Token created.')
    return token


@app.route(f'{routes.USERS}', methods=['POST'])
def create_user():
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

    else:
        user_id = service.create_user(user)
        listener_logger.info(f'User "{user.username}" created with id {user_id}')
        return jsonify({'user_id': user_id}), 201


@app.route(f'{routes.USERS}', methods=['GET'])
def get_user():
    listener_logger.info('Get user.')
    if username := request.args.get('username'):
        user_id = service.get_user_id_by_username(username)
    else:
        listener_logger.error('Field "username" is missing.')
        return settings.VALIDATION_ERROR, 400

    if user_id:
        listener_logger.debug(f'User found: {user_id}')
        return jsonify({'user_id': user_id})
    else:
        listener_logger.error(f'User "{username}" not found.')
        return f'User "{username}" not found.', 404


@app.route(f'{routes.USERS}', methods=['DELETE'])
def delete_user():
    listener_logger.info('Delete user.')

    if user_id := request.json.get('user_id'):
        service.delete_user(user_id)
        listener_logger.debug(f'User deleted: {user_id}')
        return 'User deleted.', 200

    else:
        listener_logger.error('Field "user_id" is missing.')
        return settings.VALIDATION_ERROR, 400


@app.route(routes.LOGIN, methods=['POST'])
def login():
    listener_logger.info('Login request.')
    listener_logger.debug(f'Request: {request.json}')

    try:
        user = UserLogin(**request.json)
    except ValidationError as e:
        listener_logger.error(f'Login validation caused error: {e}')
        return settings.VALIDATION_ERROR, 400

    exp_password = hdd_db_handler.get_user_password(user.username)
    if exp_password and exp_password == user.password:
        listener_logger.debug(f'Login successful for username: {user.username}')

        user_id = service.get_user_id_by_username(user.username)
        ram_db_handler.insert_username(user_id, user.username)

        service.store_user_address(user_id, user.user_address)
        service.put_login_in_queue(user_id, user.user_address)
        token = create_token(user.username)

        listener_logger.debug(f'User id "{user_id}" logged in with token "{token}".')
        listener_logger.debug(f'User id "{user_id}" logged in with address "{user.user_address}".')
        return jsonify({'msg': 'Login successful.', 'user_id': user_id, 'token': token})

    else:
        listener_logger.error('Incorrect username or password.')
        return 'Incorrect username or password.', 401


@app.route(routes.MESSAGES, methods=['POST'])
def process_messages():
    listener_logger.info('Messages request.')
    listener_logger.debug(f'Request: {request.json}')

    try:
        msg = Message(**request.json)
    except ValidationError as e:
        listener_logger.error(f'Message validation caused error: {e}')
        return settings.VALIDATION_ERROR, 400

    error = check_token(request.headers)
    if error:
        return error

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

    else:
        listener_logger.error('Invalid username.')
        return settings.NOT_AUTHORIZED, 401


@app.route(routes.HEALTH, methods=['HEAD'])
def health_check():
    listener_logger.info('Health checked for other services.')
    return 'OK', 200


if __name__ == '__main__':
    listener_logger.info('Listener started.')

    try:
        app.run(host=settings.REST_API_HOST, port=settings.REST_API_PORT, debug=True, use_reloader=False, threaded=True)
    except Exception as e:
        listener_logger.info(f'Listener failed with unexpected error:\n{e}.')

    listener_logger.info('Listener ended.')
