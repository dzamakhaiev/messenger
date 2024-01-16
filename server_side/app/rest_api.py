import requests
import settings

from threading import Thread
from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse

from server_side.database.db_handler import DatabaseHandler


TASK_MANAGER_URL = f'http://{settings.LOCAL_HOST}:{settings.TASK_API_PORT}{settings.TASK_RESOURCE}'
db = DatabaseHandler()


def user_in_db(user_id):
    return db.is_user_exists(user_id=user_id)


class User(Resource):

    def get(self):
        return 'Test GET method', 200

    def put(self):
        return 'Test PUT method', 201

    def post(self):
        return 'Test POST method', 201

    def delete(self):
        return 'Test DELETE method', 200


class Message(Resource):

    def get(self):
        return 'Test GET method', 200

    def put(self):
        return 'Test PUT method', 201

    def post(self):
        json_dict = request.json

        # TODO: add json validator
        if json_dict.get('message') and json_dict.get('sender_id') and json_dict.get('receiver_id'):

            # TODO: add response code
            if user_in_db(json_dict['sender_id']) and user_in_db(json_dict['receiver_id']):

                sender_address = f"http://{request.environ['REMOTE_ADDR']}:{request.environ['REMOTE_PORT']}"
                new_json_dict = dict(**json_dict)
                new_json_dict['sender_address'] = sender_address

                try:
                    send_task = Thread(
                        target=lambda: requests.post(TASK_MANAGER_URL, json=new_json_dict), daemon=True)
                    send_task.start()
                except requests.exceptions.ConnectionError:
                    # TODO: add response code
                    pass

        return 'Test POST method', 201

    def delete(self):
        return 'Test DELETE method', 200


if __name__ == '__main__':
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Message, settings.MESSAGE_RESOURCE)
    api.add_resource(User, settings.USER_RESOURCE)
    app.run(host=settings.LOCAL_HOST, port=settings.REST_API_PORT, debug=True, use_reloader=False, threaded=False)
