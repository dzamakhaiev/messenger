import os
import sys
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
from server_side.app.models import UserLogin, Message

app = Flask(__name__)
hdd_db_handler = HDDDatabaseHandler()
ram_db_handler = RAMDatabaseHandler()
hdd_db_handler.create_all_tables()
ram_db_handler.create_all_tables()
service = Service(hdd_db_handler, ram_db_handler)


@app.route(routes.LOGIN, methods=['POST'])
def login():
    try:
        user = UserLogin(**request.json)
    except ValidationError as e:
        return settings.VALIDATION_ERROR, 400

    exp_password = hdd_db_handler.get_user_password(user.username)
    if exp_password and exp_password == user.password:

        user_id = service.get_user_id_by_username(user.username)
        ram_db_handler.insert_username(user_id, user.username)  # store it in ram for further checks
        session_id = service.get_or_create_user_session(user_id)
        service.store_user_address_and_session(user_id, session_id, user.user_address)

        # Check not received messages for current user
        messages = service.get_messages(user_id)
        if messages:
            address_list = service.get_user_address(user_id)
            service.send_messages_by_list(address_list, messages)

        return jsonify({'msg': 'Login successful.', 'user_id': user_id, 'session_id': session_id})

    else:
        return f'Incorrect username or password.', 401


@app.route(f'{routes.USERS}', methods=['POST'])
def get_user_id():
    session_id = request.json.get('session_id')
    if not service.check_session_exists(session_id):
        return settings.NOT_AUTHORIZED, 401

    if username := request.json.get('username'):
        user_id = service.get_user_id_by_username(username)
    else:
        return settings.VALIDATION_ERROR, 400

    if user_id:
        return jsonify({'user_id': user_id})
    else:
        return f'User "{username}" not found', 404


@app.route(routes.MESSAGES, methods=['POST'])
def receive_msg():
    try:
        msg = Message(**request.json)
    except ValidationError as e:
        return settings.VALIDATION_ERROR, 400

    if not service.check_user_id(msg.receiver_id):
        return settings.VALIDATION_ERROR, 400

    username = service.get_username_by_user_id(msg.sender_id)
    session_id = service.get_session_id(msg.sender_id)

    if msg.session_id == session_id and msg.sender_username == username:
        address_list = service.get_user_address(msg.receiver_id)
        service.send_message_by_list(address_list, request.json)
        return settings.SUCCESSFUL, 200

    else:
        return settings.NOT_AUTHORIZED, 401


if __name__ == '__main__':
    app.run(host=settings.REST_API_HOST, port=settings.REST_API_PORT, debug=True)
