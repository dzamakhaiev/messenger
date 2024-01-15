from flask import Flask
from flask_restful import Api, Resource, reqparse


class Messenger(Resource):

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
    api.add_resource(Messenger, "/")
    app.run(debug=True)
