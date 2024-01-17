import settings
from threading import Thread
from flask import Flask, request
from flask_restful import Api, Resource


class Task(Resource):

    def post(self):
        json_dict = request.json
        return 'Test POST method', 201


if __name__ == '__main__':
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Task, settings.LISTENER_RESOURCE)

    task_thread = Thread(daemon=True,
                         target=lambda: app.run(host=settings.LISTENER_HOST,
                                                port=settings.LISTENER_PORT,
                                                debug=False,
                                                threaded=True,
                                                use_reloader=False))
    task_thread.start()
