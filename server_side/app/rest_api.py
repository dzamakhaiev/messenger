from threading import Thread
import requests
from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse
import settings

TASK_MANAGER_URL = f'http://{settings.LOCAL_HOST}:{settings.TASK_API_PORT}{settings.TASK_RESOURCE}'


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

        if json_dict.get('message'):
            sender_address = f"{request.environ['REMOTE_ADDR']}:{request.environ['REMOTE_PORT']}"
            new_json_dict = {'json': json_dict, 'sender_address': sender_address}

            try:
                send_task = Thread(
                    target=lambda: requests.post(TASK_MANAGER_URL, json=new_json_dict), daemon=True)
                send_task.start()
            except requests.exceptions.ConnectionError:
                pass

        return 'Test POST method', 201

    def delete(self):
        return 'Test DELETE method', 200


if __name__ == '__main__':
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Message, settings.MESSAGE_RESOURCE)
    api.add_resource(User, settings.USER_RESOURCE)
    app.run(host=settings.LOCAL_HOST, port=settings.REST_API_PORT, debug=True, use_reloader=False)
