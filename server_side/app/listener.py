import os
import sys
import logging
import routes
import settings
from pydantic import ValidationError
from flask import Flask, request, jsonify

# I hate python imports. Fix for run via cmd inside venv
current_file = os.path.realpath(__file__)
current_dir = os.path.dirname(current_file)
repo_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, repo_dir)

from server_side.database.db_handler import HDDDatabaseHandler, RAMDatabaseHandler
from server_side.app.service import Service
from server_side.app.models import UserLogin, User, Message


logging.basicConfig(format=settings.LOG_FORMAT)
app = Flask(__name__)

# Set up DB handlers
hdd_db_handler = HDDDatabaseHandler()
ram_db_handler = RAMDatabaseHandler()
hdd_db_handler.create_all_tables()
ram_db_handler.create_all_tables()
service = Service(hdd_db_handler, ram_db_handler)


def create_user(request_json: dict):
    try:
        user = User(**request_json)
    except ValidationError as e:
        return settings.VALIDATION_ERROR, 400

    username = hdd_db_handler.get_user(username=user.username)
    if username:
        return 'Username already exists.', 400
    else:
        user_id = service.create_user(user)
        return jsonify({'user_id': user_id}), 201


def get_user(request_json: dict):

    if username := request_json.get('username'):
        user_id = service.get_user_id_by_username(username)
    else:
        return settings.VALIDATION_ERROR, 400

    if user_id:
        return jsonify({'user_id': user_id})
    else:
        return f'User "{username}" not found', 404


@app.route(routes.LOGIN, methods=['POST'])
def login():
    try:
        user = UserLogin(**request.json)
    except ValidationError as e:
        return settings.VALIDATION_ERROR, 400

    exp_password = hdd_db_handler.get_user_password(user.username)
    if exp_password and exp_password == user.password:
        user_id = service.get_user_id_by_username(user.username)
        app.logger.info(f'User "{user.username}" with user id "{user_id}" logged in.')

        ram_db_handler.insert_username(user_id, user.username)  # store it in ram for further checks
        session_id = service.get_or_create_user_session(user_id)
        service.store_user_address_and_session(user_id, session_id, user.user_address)

        # Check not received messages for current user
        messages = service.get_messages(user_id)
        if messages:
            address_list = service.get_user_address(user_id)
            app.logger.info(f'Send messages to "{user_id}" user id after log in.')
            service.send_messages_by_list(address_list, messages)

        return jsonify({'msg': 'Login successful.', 'user_id': user_id, 'session_id': session_id})

    else:
        return f'Incorrect username or password.', 401


@app.route(f'{routes.USERS}', methods=['POST'])
def users():
    if request.json.get('request') and request.json.get('request') == 'create_user':
        return create_user(request.json)

    elif request.json.get('request') and request.json.get('request') == 'get_user':

        session_id = request.json.get('session_id')
        if not service.check_session_exists(session_id):
            return settings.NOT_AUTHORIZED, 401
        return get_user(request.json)

    else:
        return settings.VALIDATION_ERROR, 400


@app.route(routes.MESSAGES, methods=['POST'])
def process_messages():
    try:
        msg = Message(**request.json)
    except ValidationError as e:
        app.logger.error(e)
        return settings.VALIDATION_ERROR, 400

    if not service.check_user_id(msg.receiver_id):
        app.logger.error(f'User id "{msg.receiver_id}" not found.')
        return settings.VALIDATION_ERROR, 400

    username = service.get_username_by_user_id(msg.sender_id)
    session_id = service.get_session_id(msg.sender_id)

    if msg.session_id == session_id and msg.sender_username == username:
        address_list = service.get_user_address(msg.receiver_id)
        app.logger.info(f'Send message to "{msg.receiver_id}" user id.')

        msg_state = service.send_message_by_list(address_list, request.json)
        state = 'received' if msg_state else 'sent'
        return settings.MESSAGE_STATE.format(state), 200

    else:
        return settings.NOT_AUTHORIZED, 401


if __name__ == '__main__':
    app.run(host=settings.REST_API_HOST, port=settings.REST_API_PORT, debug=True, use_reloader=False)
