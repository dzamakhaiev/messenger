from flask import Flask, request, jsonify
import uuid
import routes
import settings
from server_side.database.db_handler import DatabaseHandler, RAMDatabaseHandler

app = Flask(__name__)
db_handler = DatabaseHandler()
ram_db_handler = RAMDatabaseHandler()
ram_db_handler.create_all_tables()


@app.route(routes.LOGIN, methods=['POST'])
def login():

    if request.json.get('username') and request.json.get('password'):
        username = request.json['username']
        password = request.json['password']
        exp_password = db_handler.get_user_password(username)

        if exp_password and exp_password == password:

            user_id = db_handler.get_user_id_by_username(username)
            exists_session = ram_db_handler.get_user_session(user_id)
            session_id = exists_session if exists_session else str(uuid.uuid4())
            ram_db_handler.insert_session_id(user_id, session_id)

            user_address = request.json['user_address']
            ram_db_handler.insert_user_address(user_id, user_address)
            return jsonify({'msg': 'Login successful.', 'user_id': user_id, 'session_id': session_id})

        else:
            return f'Incorrect username or password.', 401


@app.route(f'{routes.USERS}<username>', methods=['GET'])
def get_user_id(username):
    user_id = db_handler.get_user_id_by_username(username)

    if user_id:
        return jsonify({'user_id': user_id})
    else:
        return f'User "{username}" not found', 404


@app.route(routes.MESSAGES, methods=['POST'])
def receive_msg():

    if request.json.get('sender_id'):
        sender_id = request.json.get('sender_id')
        session_id = ram_db_handler.get_user_session(sender_id)

    else:
        return f'Invalid request.', 400

    if request.json.get('session_id') == session_id:
        receiver_id = request.json.get('receiver_id')
        address_list = ram_db_handler.get_user_address(receiver_id)

    else:
        return f'Not authorized.', 400

    if address_list:
        pass
    else:
        return f'Message sent.', 200


if __name__ == '__main__':
    app.run(host=settings.REST_API_HOST, port=settings.REST_API_PORT, debug=True, use_reloader=False, threaded=False)
