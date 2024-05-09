import requests
from queue import Queue
from threading import Thread, Event


def send_message(url, msg_json):
    try:
        response = requests.post(url, json=msg_json)
        return response
    except requests.exceptions.ConnectionError:
        pass


def send_message_by_list(address_list, msg_json):
    for user_address in address_list:
        try:
            send_message(user_address, msg_json)
        except Exception as e:
            print(e)


class MessagesManager:

    def __init__(self, queue: Queue):
        self.queue = queue

    def run_inf_loop(self, stop_event: Event):
        while True:
            try:
                if stop_event.is_set():
                    break

                if not self.queue.empty():
                    item = self.queue.get()

                    if isinstance(item, tuple):
                        address_list, msg_json = item
                        send_message_by_list(address_list, msg_json)

            except KeyboardInterrupt:
                break
