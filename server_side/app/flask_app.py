from flask import Flask
from flask_restful import Api, Resource, reqparse


class Messenger(Resource):

    def get(self):
        pass

    def put(self):
        pass

    def post(self):
        pass

    def delete(self):
        pass


if __name__ == '__main__':
    app = Flask(__name__)
    api = Api(app)
    app.run(debug=True)
