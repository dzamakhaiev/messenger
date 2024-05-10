import requests
from time import sleep
from queue import Queue
from threading import Thread, Event
from server_side.database.db_handler import RAMDatabaseHandler


ram_db_handler = RAMDatabaseHandler()
ram_db_handler.create_messages_table()


def send_message(url, msg_json):
    try:
        response = requests.post(url, json=msg_json)
        return response
    except requests.exceptions.ConnectionError:
        pass


def send_message_by_list(address_list, msg_json):
    message_received = False

    for user_address in address_list:
        try:
            response = send_message(user_address, msg_json)
            if response and response.status_code == 200:
                message_received = True

        except Exception as e:  # debug only
            print(e)

    if not message_received:
        store_message_to_db(msg_json)
    return message_received


def store_message_to_db(msg_json):
    ram_db_handler.insert_message(msg_json.get('sender_id'),
                                  msg_json.get('receiver_id'),
                                  msg_json.get('sender_username'),
                                  msg_json.get('message'))


def send_messages_by_list(address_list, messages):
    messages_to_delete = []

    for message in messages:
        msg_id, sender_id, receiver_id, sender_username, msg, msg_date = message
        msg_json = {'message': msg, 'sender_id': sender_id, 'sender_username': sender_username,
                    'receiver_id': receiver_id}
        msg_received = send_message_by_list(address_list, msg_json)

        if msg_received:
            messages_to_delete.append(msg_id)

    messages_to_delete = ','.join([str(msg) for msg in messages_to_delete])
    ram_db_handler.delete_messages(messages_to_delete)


class MessagesManager:

    def __init__(self, queue: Queue):
        self.queue = queue

    def run_inf_loop(self, stop_event: Event):
        while True:
            try:
                sleep(0.1)  # reduce cpu load from infinite loop

                if stop_event.is_set():
                    break

                if not self.queue.empty():
                    item = self.queue.get()
                    item_type, payload = item

                    if item_type == 'message':
                        address_list, msg_json = payload
                        send_message_by_list(address_list, msg_json)

                    elif item_type == 'user':
                        user_id, address_list = payload
                        messages = ram_db_handler.get_user_messages(user_id)
                        send_messages_by_list(address_list, messages)

            except KeyboardInterrupt:
                break
