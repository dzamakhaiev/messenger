import os
import json
from copy import copy
from datetime import datetime
from unittest import TestCase, skipIf, mock
from scripts.get_container_info import docker_is_running, container_is_running
from server_side.app import listener
from server_side.app import settings
from server_side.app import routes
from tests import test_data

app = listener.app

RUN_INSIDE_DOCKER = int(os.environ.get('RUN_INSIDE_DOCKER', 0))
CI_RUN = int(os.environ.get('CI_RUN', 0))
CONTAINER_NAME = 'rabbitmq-ci' if CI_RUN else 'rabbitmq'
DOCKER_RUNNING = docker_is_running()
CONTAINER_RUNNING = container_is_running(CONTAINER_NAME)
CONDITION = not (DOCKER_RUNNING and CONTAINER_RUNNING)
REASON = f'Docker/{CONTAINER_NAME} container is not running'

CONTAINER_NAME2 = 'postgres-ci' if CI_RUN else 'postgres'
DOCKER_RUNNING2 = docker_is_running()
CONTAINER_RUNNING2 = container_is_running(CONTAINER_NAME2)
CONDITION2 = not (DOCKER_RUNNING2 and CONTAINER_RUNNING2)
REASON2 = f'Docker/{CONTAINER_NAME2} container is not running'


class TestListener(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = listener.service
        cls.users = {}
        cls.user = None

        #  tables in HDD database
        query = 'GRANT ALL ON SCHEMA public TO postgres; GRANT ALL ON SCHEMA public TO public;'
        cls.service.hdd_db_handler.cursor_with_commit(query, [])

        cls.service.ram_db_handler.create_all_tables()
        cls.service.hdd_db_handler.create_all_tables()

    def setUp(self):
        app.config.update({'TESTING': True})
        self.flask_client = app.test_client()
        self.create_user_json = {'username': test_data.USERNAME,
                                 'phone_number': test_data.PHONE_NUMBER,
                                 'password': test_data.PASSWORD}
        self.msg_json = {'message': 'test', 'sender_id': None,
                         'sender_username': None, 'receiver_id': None,
                         'send_date': datetime.now().strftime(settings.DATETIME_FORMAT)}

    def create_user(self):
        user = listener.User(**test_data.USER_CREATE_JSON)
        user_id = self.service.create_user(user)
        self.users[user_id] = user
        self.user = user
        return user_id

    @staticmethod
    def convert_json_to_get_args(json_dict: dict):
        args = '?'
        if json_dict and len(json_dict) > 1:
            args += '&'.join([f'{key}={value}' for key, value in json_dict.items()])
        elif json_dict and len(json_dict) == 1:
            args += '{}={}'.format(list(json_dict.keys())[0], list(json_dict.values())[0])
        return args

    @skipIf(CONDITION, REASON)
    @skipIf(CONDITION2, REASON2)
    def test_create_token(self):
        # Preconditions and test data
        user_id = self.create_user()

        # Create token for created user
        token = listener.create_token(user_id=user_id, username=self.user.username)
        self.assertTrue(token)
        self.assertTrue(isinstance(token, str))

        # Check that token exists in databases
        token_db = self.service.get_user_token(user_id=user_id)
        self.assertEqual(token, token_db)

    @skipIf(CONDITION, REASON)
    @skipIf(CONDITION2, REASON2)
    def test_check_token(self):

        # Preconditions and test data
        user_id = self.create_user()
        token = listener.create_token(user_id=user_id, username=self.user.username)

        # Case 1: check_token returns None, None for valid token
        with app.test_request_context(headers={'Authorization': f'Bearer {token}'}):
            result_tuple = listener.check_token()
            self.assertEqual(result_tuple, (None, None))

        # Case 2: check no token
        with app.test_request_context(headers={'Authorization': ''}):
            error_tuple = listener.check_token()
            self.assertEqual(error_tuple, (settings.NOT_AUTHORIZED, 401))

        # Case 3: compare two different, but valid tokes
        with app.test_request_context(headers={'Authorization': f'Bearer {token}'}):
            with mock.patch('server_side.app.listener.settings.TOKEN_EXP_MINUTES', 666):
                self.service.delete_user_token(user_id=user_id)
                another_token = listener.create_token(user_id=user_id, username=self.user.username)
            error_tuple = listener.check_token()
            self.assertEqual(error_tuple, (settings.NOT_AUTHORIZED, 401))

        # Case 4: check expired token
        with mock.patch('server_side.app.listener.settings.TOKEN_EXP_MINUTES', -60 * 24):
            token = listener.create_token(user_id=user_id, username=self.user.username)
        with app.test_request_context(headers={'Authorization': f'Bearer {token}'}):
            error_tuple = listener.check_token()
            self.assertEqual(error_tuple, (settings.INVALID_TOKEN, 401))

        # Case 5: check invalid token
        with app.test_request_context(headers={'Authorization': 'Bearer invalid_token'}):
            error_tuple = listener.check_token()
            self.assertEqual(error_tuple, (settings.INVALID_TOKEN, 401))

    @skipIf(CONDITION, REASON)
    @skipIf(CONDITION2, REASON2)
    def test_create_user(self):

        # Case 1: valid user json
        with self.flask_client as client:
            response = client.post(routes.USERS,
                                   data=json.dumps(self.create_user_json),
                                   content_type='application/json')
            self.assertEqual(response.status_code, 201)
            self.users[response.json.get('user_id')] = copy(self.create_user_json)

        # Case 2: invalid user json
        with self.flask_client as client:
            user_json = copy(self.create_user_json)
            user_json.pop('password')

            response = client.post(routes.USERS,
                                   data=json.dumps(user_json),
                                   content_type='application/json')
            self.assertEqual(response.status_code, 400)

        # Case 3: user already exists
        with self.flask_client as client:
            response = client.post(routes.USERS,
                                   data=json.dumps(self.create_user_json),
                                   content_type='application/json')
            self.assertEqual(response.status_code, 400)

    @skipIf(CONDITION, REASON)
    @skipIf(CONDITION2, REASON2)
    def test_get_user(self):
        # Test data
        user_id = self.create_user()

        # Case 1: valid user json without token
        with self.flask_client as client:
            endpoint = routes.USERS + self.convert_json_to_get_args(
                {'username': self.user.username})
            response = client.get(endpoint, content_type='application/json')
            self.assertEqual(response.status_code, 401)

        # Case 2: valid user json with token
        token = listener.create_token(user_id=user_id, username=self.user.username)

        with self.flask_client as client:
            endpoint = routes.USERS + self.convert_json_to_get_args(
                {'username': self.user.username})
            response = client.get(endpoint, content_type='application/json',
                                  headers={'Authorization': f'Bearer {token}'})

            self.assertEqual(response.status_code, 200)

        # Case 3: non-exists user
        with self.flask_client as client:
            endpoint = routes.USERS + self.convert_json_to_get_args(
                {'username': test_data.USERNAME_2})
            response = client.get(endpoint, content_type='application/json',
                                  headers={'Authorization': f'Bearer {token}'})

            self.assertEqual(response.status_code, 404)

        # Case 4: invalid user json with token
        token = listener.create_token(user_id=user_id, username=self.user.username)
        with self.flask_client as client:
            response = client.get(routes.USERS, content_type='application/json',
                                  headers={'Authorization': f'Bearer {token}'})
            self.assertEqual(response.status_code, 400)

    @skipIf(CONDITION, REASON)
    @skipIf(CONDITION2, REASON2)
    def test_delete_user(self):
        # Test data
        user_id = self.create_user()

        # Case 1: valid json
        with self.flask_client as client:
            response = client.delete(routes.USERS,
                                     data=json.dumps({'user_id': user_id}),
                                     content_type='application/json')
            self.assertEqual(response.status_code, 200)

        # Case 2: invalid json
        with self.flask_client as client:
            response = client.delete(routes.USERS,
                                     data=json.dumps({}),
                                     content_type='application/json')
            self.assertEqual(response.status_code, 400)

        # Case 3: non-exists user
        with self.flask_client as client:
            self.service.delete_user_token(user_id=user_id)
            response = client.delete(routes.USERS,
                                     data=json.dumps({'user_id': user_id}),
                                     content_type='application/json')
            self.assertEqual(response.status_code, 200)

    @skipIf(CONDITION, REASON)
    @skipIf(CONDITION2, REASON2)
    def test_login(self):
        # Test data
        self.create_user()

        # Case 1: valid user login json
        with self.flask_client as client:
            response = client.post(routes.LOGIN,
                                   data=json.dumps({'username': self.user.username,
                                                    'password': self.user.password,
                                                    'user_address': test_data.USER_ADDRESS,
                                                    'public_key': test_data.USER_PUBLIC_KEY}),
                                   content_type='application/json')
            self.assertEqual(response.status_code, 200)

        # Case 2: invalid user login json
        with self.flask_client as client:
            response = client.post(routes.LOGIN,
                                   data=json.dumps({'username': self.user.username,
                                                    'password': self.user.password}),
                                   content_type='application/json')
            self.assertEqual(response.status_code, 400)

        # Case 3: incorrect password
        with self.flask_client as client:
            response = client.post(routes.LOGIN,
                                   data=json.dumps({'username': self.user.username,
                                                    'password': 'some password',
                                                    'user_address': test_data.USER_ADDRESS,
                                                    'public_key': test_data.USER_PUBLIC_KEY}),
                                   content_type='application/json')
            self.assertEqual(response.status_code, 401)

        # Case 4: incorrect username
        with self.flask_client as client:
            response = client.post(routes.LOGIN,
                                   data=json.dumps({'username': test_data.USERNAME_2,
                                                    'password': self.user.password,
                                                    'user_address': test_data.USER_ADDRESS,
                                                    'public_key': test_data.USER_PUBLIC_KEY}),
                                   content_type='application/json')
            self.assertEqual(response.status_code, 401)

    @skipIf(CONDITION, REASON)
    @skipIf(CONDITION2, REASON2)
    def test_logout(self):
        # Test data
        user_id = self.create_user()

        # Case 1: valid user json without token
        with self.flask_client as client:
            response = client.post(routes.LOGOUT,
                                   data=json.dumps({'username': self.user.username}),
                                   content_type='application/json')
            self.assertEqual(response.status_code, 401)

        # Case 2: invalid user json without token
        token = listener.create_token(user_id=user_id, username=self.user.username)

        with self.flask_client as client:
            response = client.post(routes.LOGOUT,
                                   data=json.dumps({}),
                                   content_type='application/json',
                                   headers={'Authorization': f'Bearer {token}'})
            self.assertEqual(response.status_code, 400)

        # Case 3: invalid username with valid token
        with self.flask_client as client:
            response = client.post(routes.LOGOUT,
                                   data=json.dumps({'username': test_data.USERNAME_2}),
                                   content_type='application/json',
                                   headers={'Authorization': f'Bearer {token}'})
            self.assertEqual(response.status_code, 400)

        # Case 4: valid user json with token
        with self.flask_client as client:
            response = client.post(routes.LOGOUT,
                                   data=json.dumps({'username': self.user.username}),
                                   content_type='application/json',
                                   headers={'Authorization': f'Bearer {token}'})
            self.assertEqual(response.status_code, 200)

    @skipIf(CONDITION, REASON)
    @skipIf(CONDITION2, REASON2)
    def test_process_messages(self):
        # Test data
        sender_user_id = self.create_user()
        receiver_user_id = self.create_user()

        self.msg_json['sender_id'] = sender_user_id
        self.msg_json['receiver_id'] = receiver_user_id
        self.msg_json['sender_username'] = self.users[sender_user_id].username

        # Case 1: valid msg json without token
        with self.flask_client as client:
            response = client.post(routes.MESSAGES,
                                   data=json.dumps(self.msg_json),
                                   content_type='application/json')
            self.assertEqual(response.status_code, 401)

        # Case 2: valid msg json with token
        token = listener.create_token(user_id=sender_user_id, username=self.user.username)

        with self.flask_client as client:
            response = client.post(routes.MESSAGES,
                                   data=json.dumps(self.msg_json),
                                   content_type='application/json',
                                   headers={'Authorization': f'Bearer {token}'})
            self.assertEqual(response.status_code, 200)

        # Case 3: invalid msg json with token
        token = listener.create_token(user_id=sender_user_id, username=self.user.username)

        with self.flask_client as client:
            msg_json = copy(self.msg_json)
            msg_json.popitem()

            response = client.post(routes.MESSAGES,
                                   data=json.dumps(msg_json),
                                   content_type='application/json',
                                   headers={'Authorization': f'Bearer {token}'})
            self.assertEqual(response.status_code, 400)

        # Case 4: invalid receiver_id json with token
        token = listener.create_token(user_id=sender_user_id, username=self.user.username)

        with self.flask_client as client:
            msg_json = copy(self.msg_json)
            msg_json['receiver_id'] = -1

            response = client.post(routes.MESSAGES,
                                   data=json.dumps(msg_json),
                                   content_type='application/json',
                                   headers={'Authorization': f'Bearer {token}'})
            self.assertEqual(response.status_code, 400)

        # Case 5: sender user_id does not match sender username
        token = listener.create_token(user_id=sender_user_id, username=self.user.username)

        with self.flask_client as client:
            msg_json = copy(self.msg_json)
            msg_json['sender_username'] = test_data.USERNAME_2

            response = client.post(routes.MESSAGES,
                                   data=json.dumps(msg_json),
                                   content_type='application/json',
                                   headers={'Authorization': f'Bearer {token}'})
            self.assertEqual(response.status_code, 401)

    @skipIf(CONDITION, REASON)
    @skipIf(CONDITION2, REASON2)
    def test_health_check(self):

        with self.flask_client as client:
            response = client.head(routes.HEALTH)
            self.assertEqual(response.status_code, 200)

    def tearDown(self):
        if self.users:
            for user_id in self.users:
                self.service.delete_user(user_id=user_id)

    @classmethod
    def tearDownClass(cls):
        # Drop all tables in HDD database
        query = "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
        cls.service.hdd_db_handler.cursor_with_commit(query, [])
