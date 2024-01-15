from queue import Queue
from flask import Flask
from flask_restful import Api, Resource, reqparse


class User(Resource):

    def get(self):
        return 'Test GET method', 200

    def put(self):
        return 'Test PUT method', 201

    def post(self):
        return 'Test POST method', 201

    def delete(self):
        return 'Test DELETE method', 200


class Messages(Resource):

    def get(self):
        return 'Test GET method', 200

    def put(self):
        return 'Test PUT method', 201

    def post(self):
        return 'Test POST method', 201

    def delete(self):
        return 'Test DELETE method', 200


if __name__ == '__main__':
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Messages, "/messages")
    api.add_resource(User, "/user")
    app.run(debug=True)
