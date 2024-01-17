import requests
import settings

from time import sleep
from queue import Queue
from threading import Thread
from flask import Flask, request
from flask_restful import Api, Resource

from server_side.database.db_handler import DatabaseHandler

INITIAL_INTERVAL = 1
MAX_INTERVAL = 60
CHECK_NUMBER = 10
queue = Queue()


class Task(Resource):

    def post(self):
        json_dict = request.json
        if json_dict:

            if json_dict.get('message'):
                task = ('message', json_dict)
                queue.put(task)

        return 'Test POST method', 201


class TaskManager:

    def __init__(self):
        self.queue = queue
        self.interval = INITIAL_INTERVAL
        self.count = 0
        self.db = DatabaseHandler()

    def dynamic_interval(self):
        sleep(self.interval)
        print(self.interval)
        self.count += 1

        # Increase check interval
        if self.count >= CHECK_NUMBER and self.interval < MAX_INTERVAL:
            self.interval += 5
            self.count = 0

    def reset_interval(self):
        self.interval = INITIAL_INTERVAL
        self.count = 0

    def try_send_message(self, receiver_address, message, sender_id):
        try:
            requests.post(receiver_address, json={'message': message, 'sender_id': sender_id})
            return True
        except requests.exceptions.ConnectionError:
            return False

    def check_address_list(self, address_list):
        active_address_list = [address for address, status in address_list if status == 'Active']
        return active_address_list

    def process_message_task(self, json_dict):
        message = json_dict.get('message')
        sender_id = json_dict.get('sender_id')
        receiver_id = json_dict.get('receiver_id')
        sender_address = json_dict.get('sender_address')

        # Save or update existed sender address to db
        self.db.insert_or_update_user_address(sender_id, sender_address)

        # Get receiver address list from db
        receiver_address_list = self.db.get_user_address(receiver_id)
        if receiver_address_list:
            active_address_list = self.check_address_list(receiver_address_list)

        else:
            # TODO some exception or return
            active_address_list = []

        # Try to send message to each active address
        if active_address_list:
            for receiver_address in active_address_list:
                # TODO add db data parser
                result = self.try_send_message(receiver_address, message, sender_id)
                if not result:
                    self.db.deactivate_user_address(user_id=receiver_id, user_address=receiver_address)

        else:
            pass

    def main_loop(self):

        while True:
            try:
                self.dynamic_interval()

                if not self.queue.empty():
                    print('Task is started.')
                    task = self.queue.get()
                    task_type, json_dict = task

                    if task_type == 'message':
                        self.process_message_task(json_dict)
                        self.reset_interval()

            except KeyboardInterrupt:
                break


if __name__ == '__main__':
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Task, settings.TASK_RESOURCE)

    task_thread = Thread(daemon=True,
                         target=lambda: app.run(host=settings.REST_API_HOST,
                                                port=settings.TASK_API_PORT,
                                                debug=False,
                                                threaded=True,
                                                use_reloader=False))
    task_thread.start()

    manager = TaskManager()
    manager.main_loop()
