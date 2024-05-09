import requests
from queue import Queue
from threading import Event


class MessagesManager:

    def __init__(self, queue: Queue):
        self.queue = queue

    def run_inf_loop(self, stop_event: Event):
        while True:
            try:
                if stop_event.is_set():
                    break

                if not self.queue.empty():
                    pass

            except KeyboardInterrupt:
                break
