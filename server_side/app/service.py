import uuid
import requests


class Service:

    def __init__(self, hdd_db_handler, ram_db_handler):
        self.hdd_db_handler = hdd_db_handler
        self.ram_db_handler = ram_db_handler

    @staticmethod
    def send_message(url, msg_json):
        try:
            response = requests.post(url, json=msg_json)
            return response
        except requests.exceptions.ConnectionError:
            pass

    def send_message_by_list(self, address_list, msg_json):
        message_received = False

        for user_address in address_list:
            try:
                response = self.send_message(user_address, msg_json)
                if response and response.status_code == 200:
                    message_received = True

            except Exception as e:  # debug only
                print(e)

        if not message_received:
            self.store_message_to_db(msg_json)
        return message_received

    def send_messages_by_list(self, address_list, messages):
        messages_to_delete = []

        for message in messages:
            msg_id, sender_id, receiver_id, sender_username, msg, msg_date = message
            msg_json = {'message': msg, 'sender_id': sender_id, 'sender_username': sender_username,
                        'receiver_id': receiver_id}
            msg_received = self.send_message_by_list(address_list, msg_json)

            if msg_received:
                messages_to_delete.append(msg_id)

        messages_to_delete = ','.join([str(msg) for msg in messages_to_delete])
        self.ram_db_handler.delete_messages(messages_to_delete)

    def store_message_to_db(self, msg_json):
        self.ram_db_handler.insert_message(msg_json.get('sender_id'),
                                           msg_json.get('receiver_id'),
                                           msg_json.get('sender_username'),
                                           msg_json.get('message'))

    def store_user_address_and_session(self, user_id, session_id, user_address):
        # Store user data in both DBs for back up
        self.ram_db_handler.insert_session_id(user_id, session_id)
        self.hdd_db_handler.insert_session_id(user_id, session_id)
        self.ram_db_handler.insert_user_address(user_id, user_address)
        self.hdd_db_handler.insert_user_address(user_id, user_address)

    def get_or_create_user_session(self, user_id):
        session_id = self.get_session_id(user_id)

        if session_id:
            return session_id
        else:
            return str(uuid.uuid4())

    def get_session_id(self, user_id):
        session_id = self.ram_db_handler.get_user_session(user_id)
        if session_id:
            return session_id
        else:
            return self.hdd_db_handler.get_user_session(user_id)

    def get_user_id_by_username(self, username):
        user_id = self.ram_db_handler.get_user_id(username)
        if not user_id:
            user_id = self.hdd_db_handler.get_user_id(username)

        return user_id

    def get_username_by_user_id(self, user_id):
        username = self.ram_db_handler.get_username(user_id)
        if not username:
            username = self.hdd_db_handler.get_username(user_id)

        if username:
            return username
        else:
            return ''

    def get_user_address(self, user_id):
        address_list = self.ram_db_handler.get_user_address(user_id)
        if not address_list:
            address_list = self.hdd_db_handler.get_user_address(user_id)

        return address_list

    def check_session_exists(self, session_id):
        session_id = self.ram_db_handler.is_session_exists(session_id)
        if not session_id:
            session_id = self.hdd_db_handler.is_session_exists(session_id)

        if session_id:
            return True
        else:
            return False

    def check_user_id(self, user_id):
        result = self.ram_db_handler.get_user(user_id=user_id)
        if not result:
            result = self.hdd_db_handler.get_user(user_id=user_id)

        if result:
            return True
        else:
            return False
