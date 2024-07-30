from datetime import datetime

USER_ID = 1
MESSAGE_ID = 1
PASSWORD = 'qwerty'
USERNAME = 'username'
USER_TOKEN = 'some_token'
USER_PUBLIC_KEY = 'some_public_key'
USER_ADDRESS = f'https://{'192.168.0.1'}:{5000}'
USER_CREATE_JSON = {'username': 'username', 'phone_number': '1234567890', 'password': PASSWORD}
USER_MESSAGE_JSON = {'message': 'test', 'sender_id': USER_ID, 'sender_username': USERNAME,
                     'receiver_id': 2, 'send_date': datetime.now()}
