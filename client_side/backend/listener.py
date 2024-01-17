import settings
from threading import Thread
from queue import Queue
from flask import Flask, request
from flask_restful import Api, Resource


class Task(Resource):

    queue = None

    def post(self):
        json_dict = request.json
        if self.queue:
            self.queue.put(json_dict)
        return 'Test POST method', 201


def run_listener(task_queue, daemon=True):
    app = Flask(__name__)
    api = Api(app)
    Task.queue = task_queue
    api.add_resource(Task, settings.LISTENER_RESOURCE)

    task_thread = Thread(daemon=daemon,
                         target=lambda: app.run(host=settings.LISTENER_HOST,
                                                port=settings.LISTENER_PORT,
                                                debug=False,
                                                threaded=True,
                                                use_reloader=False))
    task_thread.start()


if __name__ == '__main__':
    queue = Queue()
    run_listener(queue, False)
