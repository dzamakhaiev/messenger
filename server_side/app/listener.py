import os
import sys
import uuid
import routes
import settings
from queue import Queue
from threading import Thread, Event
from pydantic import ValidationError
from flask import Flask, request, jsonify

# I hate python imports. Fix for run via cmd inside venv
current_file = os.path.realpath(__file__)
current_dir = os.path.dirname(current_file)
repo_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, repo_dir)

from server_side.database.db_handler import HDDDatabaseHandler, RAMDatabaseHandler
from server_side.app.msg_manager import MessagesManager, send_message, send_message_by_list
from server_side.app.models import UserLogin, Message

app = Flask(__name__)
queue = Queue()

hdd_db_handler = HDDDatabaseHandler()
ram_db_handler = RAMDatabaseHandler()
hdd_db_handler.create_all_tables()
ram_db_handler.create_all_tables()


def store_user_address_and_session(user_id, session_id, user_address):
    # Store user data in both DBs for back up
    ram_db_handler.insert_session_id(user_id, session_id)
    hdd_db_handler.insert_session_id(user_id, session_id)
    ram_db_handler.insert_user_address(user_id, user_address)
    hdd_db_handler.insert_user_address(user_id, user_address)


def get_or_create_user_session(user_id):
    session_id = get_session_id(user_id)

    if session_id:
        return session_id
    else:
        return str(uuid.uuid4())


def get_session_id(user_id):
    session_id = ram_db_handler.get_user_session(user_id)
    if session_id:
        return session_id
    else:
        return hdd_db_handler.get_user_session(user_id)


def get_user_id_by_username(username):
    user_id = ram_db_handler.get_user_id(username)
    if not user_id:
        user_id = hdd_db_handler.get_user_id(username)

    return user_id


def get_username_by_user_id(user_id):
    username = ram_db_handler.get_username(user_id)
    if not username:
        username = hdd_db_handler.get_username(user_id)

    if username:
        return username
    else:
        return ''


def get_user_address(user_id):
    address_list = ram_db_handler.get_user_address(user_id)
    if not address_list:
        address_list = hdd_db_handler.get_user_address(user_id)

    return address_list


def create_task_user_online(user_id):
    address_list = get_user_address(user_id)
    payload = (user_id, address_list)
    queue.put(('user', payload))


def create_task_send_msg(user_id, request_json):
    address_list = get_user_address(user_id)
    payload = (address_list, request_json)
    queue.put(('message', payload))


def check_session_exists(session_id):
    session_id = ram_db_handler.is_session_exists(session_id)
    if not session_id:
        session_id = hdd_db_handler.is_session_exists(session_id)

    if session_id:
        return True
    else:
        return False


def check_user_id(user_id):
    result = ram_db_handler.get_user(user_id=user_id)
    if not result:
        result = hdd_db_handler.get_user(user_id=user_id)

    if result:
        return True
    else:
        return False


@app.route(routes.LOGIN, methods=['POST'])
def login():
    try:
        user = UserLogin(**request.json)
    except ValidationError as e:
        return settings.VALIDATION_ERROR, 400

    exp_password = hdd_db_handler.get_user_password(user.username)
    if exp_password and exp_password == user.password:

        user_id = hdd_db_handler.get_user_id(user.username)
        ram_db_handler.insert_username(user_id, user.username)  # store it in ram for further checks
        session_id = get_or_create_user_session(user_id)
        store_user_address_and_session(user_id, session_id, user.user_address)

        # create_task_user_online(user_id)
        return jsonify({'msg': 'Login successful.', 'user_id': user_id, 'session_id': session_id})

    else:
        return f'Incorrect username or password.', 401


@app.route(f'{routes.USERS}', methods=['POST'])
def get_user_id():
    session_id = request.json.get('session_id')
    if not check_session_exists(session_id):
        return settings.NOT_AUTHORIZED, 401

    if username := request.json.get('username'):
        user_id = get_user_id_by_username(username)
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

    if not check_user_id(msg.receiver_id):
        return settings.VALIDATION_ERROR, 400

    username = get_username_by_user_id(msg.sender_id)
    session_id = get_session_id(msg.sender_id)

    if msg.session_id == session_id and msg.sender_username == username:
        # create_task_send_msg(msg.receiver_id, request.json)
        address_list = get_user_address(msg.receiver_id)
        send_message_by_list(address_list, request.json)
        return settings.SUCCESSFUL, 200

    else:
        return settings.NOT_AUTHORIZED, 401


if __name__ == '__main__':
    # msg_manager = MessagesManager(queue)
    # stop_event = Event()
    # t = Thread(target=msg_manager.run_inf_loop, args=(stop_event, ))
    # t.start()

    app.run(host=settings.REST_API_HOST, port=settings.REST_API_PORT, debug=True, use_reloader=False, threaded=False)
    # stop_event.set()
    # t.join()
