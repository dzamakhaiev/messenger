from time import sleep
from queue import Queue
from threading import Thread
from flask import Flask
from flask_restful import Api, Resource
import settings

INITIAL_INTERVAL = 1
MAX_INTERVAL = 60
CHECK_NUMBER = 10
queue = Queue()


class Task(Resource):

    def post(self):
        queue.put('Test item')
        return 'Test POST method', 201


class TaskManager:

    def __init__(self):
        self.queue = queue
        self.interval = INITIAL_INTERVAL
        self.count = 0

    def dynamic_interval(self):
        sleep(self.interval)
        print(self.interval)
        self.count += 1

        # Increase check interval
        if self.count >= CHECK_NUMBER and self.interval < MAX_INTERVAL:
            self.interval += 5
            self.count = 0

    def main_loop(self):

        while True:
            try:
                self.dynamic_interval()

                if not self.queue.empty():
                    print('Queue is not empty.')

            except KeyboardInterrupt:
                break


if __name__ == '__main__':
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Task, "/task")

    task_thread = Thread(daemon=True,
                         target=lambda: app.run(host=settings.LOCAL_HOST,
                                                port=settings.TASK_API_PORT,
                                                debug=False,
                                                threaded=True,
                                                use_reloader=False))
    task_thread.start()

    manager = TaskManager()
    manager.main_loop()
