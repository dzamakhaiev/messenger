import logging
from queue import Queue
from threading import Thread
from flask import Flask, request
from client_side.backend import settings


logging.basicConfig(format=settings.LOG_FORMAT)


def run_listener(queue: Queue, daemon=True, port=settings.LISTENER_PORT):
    app = Flask(__name__)

    @app.route('/', methods=['POST'])
    def receive_msg():
        if request.json.get('message'):
            queue.put(request.json)
            return 'Message received.', 200

    task_thread = Thread(daemon=daemon, target=lambda: app.run(host=settings.LISTENER_HOST, port=port, debug=False))
    task_thread.start()


if __name__ == '__main__':
    queue = Queue()
    run_listener(queue, False)
