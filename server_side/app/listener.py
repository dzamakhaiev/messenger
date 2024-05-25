import os
import sys
import routes
from pydantic import ValidationError
from flask import Flask, request, jsonify
from server_side.logger.logger import get_logger

# Fix for run via cmd inside venv
current_file = os.path.realpath(__file__)
current_dir = os.path.dirname(current_file)
repo_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, repo_dir)

from server_side.app import settings
from server_side.app.service import Service
from server_side.broker.mq_handler import RabbitMQHandler
from server_side.app.models import UserLogin, User, Message
from server_side.database.db_handler import HDDDatabaseHandler, RAMDatabaseHandler

# Set up listener and its logger
app = Flask(__name__)
listener_logger = get_logger('listener')

# Set up DB handlers
hdd_db_handler = HDDDatabaseHandler()
ram_db_handler = RAMDatabaseHandler()
mq_handler = RabbitMQHandler()

hdd_db_handler.create_all_tables()
ram_db_handler.create_all_tables()
mq_handler.create_exchange(settings.MQ_EXCHANGE_NAME)
mq_handler.create_and_bind_queue(settings.MQ_MSG_QUEUE_NAME)
mq_handler.create_and_bind_queue(settings.MQ_LOGIN_QUEUE_NAME)

service = Service(hdd_db_handler, ram_db_handler, mq_handler)


def create_user(request_json: dict):
    try:
        user = User(**request_json)
    except ValidationError as e:
        listener_logger.error(f'User validation caused error: {e}')
        return settings.VALIDATION_ERROR, 400

    username = hdd_db_handler.get_user(username=user.username)
    if username:
        listener_logger.error(f'Username "{username}" already exists.')
        return 'Username already exists.', 400

    else:
        user_id = service.create_user(user)
        listener_logger.info(f'User "{user.username}" created with id {user_id}')
        return jsonify({'user_id': user_id}), 201


def get_user(request_json: dict):

    if username := request_json.get('username'):
        user_id = service.get_user_id_by_username(username)
    else:
        listener_logger.error('Field "username" is missing.')
        return settings.VALIDATION_ERROR, 400

    if user_id:
        return jsonify({'user_id': user_id})
    else:
        listener_logger.error(f'User "{username}" not found.')
        return f'User "{username}" not found.', 404


def delete_user(request_json: dict):
    if user_id := request_json.get('user_id'):
        service.delete_user(user_id)
        return 'User deleted.', 200
    else:
        listener_logger.error('Field "user_id" is missing.')
        return settings.VALIDATION_ERROR, 400


def check_session(request_json: dict):
    session_id = request_json.get('session_id')
    if not service.check_session_exists(session_id):
        listener_logger.error('Incorrect session id.')
        return settings.NOT_AUTHORIZED, 401


@app.route(routes.LOGIN, methods=['POST'])
def login():
    try:
        user = UserLogin(**request.json)
    except ValidationError as e:
        listener_logger.error(f'Login validation caused error: {e}')
        return settings.VALIDATION_ERROR, 400

    exp_password = hdd_db_handler.get_user_password(user.username)
    if exp_password and exp_password == user.password:
        user_id = service.get_user_id_by_username(user.username)
        ram_db_handler.insert_username(user_id, user.username)  # store it in ram for further checks
        session_id = service.get_or_create_user_session(user_id)

        service.store_user_address_and_session(user_id, session_id, user.user_address)
        listener_logger.info(f'User id "{user_id}" logged in with session id "{session_id}".')

        return jsonify({'msg': 'Login successful.', 'user_id': user_id, 'session_id': session_id})

    else:
        listener_logger.error('Incorrect username or password.')
        return 'Incorrect username or password.', 401


@app.route(f'{routes.USERS}', methods=['POST'])
def users():
    if request.json.get('request') and request.json.get('request') == 'create_user':
        return create_user(request.json)

    elif request.json.get('request') and request.json.get('request') == 'get_user':
        if session_error := check_session(request.json):
            return session_error
        return get_user(request.json)

    elif request.json.get('request') and request.json.get('request') == 'delete_user':
        if session_error := check_session(request.json):
            return session_error
        return delete_user(request.json)

    else:
        listener_logger.error('Validation error for "/users" request.')
        return settings.VALIDATION_ERROR, 400


@app.route(routes.MESSAGES, methods=['POST'])
def process_messages():
    try:
        msg = Message(**request.json)
    except ValidationError as e:
        listener_logger.error(f'Message validation caused error: {e}')
        return settings.VALIDATION_ERROR, 400

    if not service.check_user_id(msg.receiver_id):
        listener_logger.error(f'User id "{msg.receiver_id}" not found.')
        return settings.VALIDATION_ERROR, 400

    username = service.get_username_by_user_id(msg.sender_id)
    session_id = service.get_session_id(msg.sender_id)

    if msg.session_id == session_id and msg.sender_username == username:
        listener_logger.info(f'Send message to "{msg.receiver_id}" user id.')

        address_list = service.get_user_address(msg.receiver_id)
        service.put_message_in_queue(address_list, request.json)
        return 'Message processed.', 200

    else:
        listener_logger.error('Invalid username or session id.')
        return settings.NOT_AUTHORIZED, 401


if __name__ == '__main__':
    listener_logger.info('Listener started.')

    try:
        service.restore_all_messages_from_hdd()
        app.run(host=settings.REST_API_HOST, port=settings.REST_API_PORT, debug=True, use_reloader=False, threaded=True)
    finally:
        service.store_all_messages_to_hdd()

    listener_logger.info('Listener Ended.')
