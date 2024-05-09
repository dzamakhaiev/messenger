from client_side.backend import settings
from threading import Thread
from queue import Queue
from flask import Flask, request


app = Flask(__name__)


def run_listener(queue: Queue, daemon=True):

    @app.route('/', methods=['POST'])
    def receive_msg():
        if request.json.get('message'):
            queue.put(request.json)
            return 'Message received.', 200

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
