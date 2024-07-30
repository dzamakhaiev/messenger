import hashlib
from unittest import TestCase
from tests.database_mocks import get_hdd_db_handler, get_ram_db_handler, get_mq_handler
from server_side.app.service import Service
from server_side.app.models import User
from tests import test_data


class TestUser(TestCase):

    def setUp(self):
        self.service = Service(hdd_db_handler=get_hdd_db_handler(),
                               ram_db_handler=get_ram_db_handler(),
                               mq_handler=get_mq_handler())

        self.user = User(**test_data.USER_CREATE_JSON)

    def test_user_create(self):
        # Preconditions setup
        self.service.hdd_db_handler.get_user_id.return_value = test_data.USER_ID

        # Run target method with mocked handlers
        user_id = self.service.create_user(self.user)
        self.assertEqual(user_id, test_data.USER_ID)

        # Check that internal mocked methods were called once with expected args
        password = hashlib.sha256(str(self.user.password).encode()).hexdigest()
        self.service.hdd_db_handler.insert_user.assert_called_once_with(
            self.user.username, self.user.phone_number, password)

        self.service.hdd_db_handler.get_user_id.assert_called_once_with(test_data.USERNAME)
        self.service.ram_db_handler.insert_username.assert_called_once_with(
            test_data.USER_ID, test_data.USERNAME)

    def test_store_user_address(self):
        self.service.store_user_address(test_data.USER_ID, test_data.USER_ADDRESS)

        # Check that internal mocked methods were called once with expected args
        self.service.hdd_db_handler.insert_address.assert_called_once_with(test_data.USER_ADDRESS)
        self.service.hdd_db_handler.insert_user_address.assert_called_once_with(test_data.USER_ID,
                                                                                test_data.USER_ADDRESS)
        self.service.ram_db_handler.insert_user_address.assert_called_once_with(test_data.USER_ID,
                                                                                test_data.USER_ADDRESS)

    def test_store_user_token(self):
        self.service.store_user_token(test_data.USER_ID, test_data.USER_TOKEN)

        # Check that internal mocked methods were called once with expected args
        self.service.hdd_db_handler.insert_user_token.assert_called_once_with(
            test_data.USER_ID, test_data.USER_TOKEN)
        self.service.ram_db_handler.insert_user_token.assert_called_once_with(
            test_data.USER_ID, test_data.USER_TOKEN)

    def test_store_user_public_key(self):
        self.service.store_user_public_key(test_data.USER_ID, test_data.USER_PUBLIC_KEY)

        # Check that internal mocked methods were called once with expected args
        self.service.hdd_db_handler.insert_user_public_key.assert_called_once_with(
            test_data.USER_ID, test_data.USER_PUBLIC_KEY)
        self.service.ram_db_handler.insert_user_public_key.assert_called_once_with(
            test_data.USER_ID, test_data.USER_PUBLIC_KEY)

    def test_get_user_id_by_username(self):
        # First case: get data from RAM database
        self.service.ram_db_handler.get_user_id.return_value = test_data.USER_ID
        user_id = self.service.get_user_id_by_username(test_data.USERNAME)
        self.assertEqual(user_id, test_data.USER_ID)

        # Second case: get data from HDD database
        self.service.ram_db_handler.get_user_id.return_value = None
        self.service.hdd_db_handler.get_user_id.return_value = test_data.USER_ID
        user_id = self.service.get_user_id_by_username(test_data.USERNAME)
        self.assertEqual(user_id, test_data.USER_ID)

        # Third case: no user data in both databases
        self.service.ram_db_handler.get_user_id.return_value = None
        self.service.hdd_db_handler.get_user_id.return_value = None
        user_id = self.service.get_user_id_by_username(test_data.USERNAME)
        self.assertTrue(user_id is None)

        # Check that internal mocked methods were called once with expected args
        self.service.hdd_db_handler.get_user_id.assert_any_call(test_data.USERNAME)
        self.service.ram_db_handler.get_user_id.assert_any_call(test_data.USERNAME)

    def test_get_username_by_user_id(self):
        # First case: get data from RAM database
        self.service.ram_db_handler.get_username.return_value = test_data.USERNAME
        username = self.service.get_username_by_user_id(test_data.USER_ID)
        self.assertEqual(username, test_data.USERNAME)

        # Second case: get data from HDD database
        self.service.ram_db_handler.get_username.return_value = None
        self.service.hdd_db_handler.get_username.return_value = test_data.USERNAME
        username = self.service.get_username_by_user_id(test_data.USER_ID)
        self.assertEqual(username, test_data.USERNAME)

        # Third case: no user data in both databases
        self.service.ram_db_handler.get_username.return_value = None
        self.service.hdd_db_handler.get_username.return_value = None
        username = self.service.get_username_by_user_id(test_data.USER_ID)
        self.assertEqual(username, '')

        # Check that internal mocked methods were called once with expected args
        self.service.hdd_db_handler.get_username.assert_any_call(test_data.USER_ID)
        self.service.ram_db_handler.get_username.assert_any_call(test_data.USER_ID)

    def test_get_user_address(self):
        # First case: get data from RAM database
        self.service.ram_db_handler.get_user_address.return_value = [test_data.USER_ADDRESS]
        user_addresses = self.service.get_user_address(test_data.USER_ID)
        self.assertEqual(user_addresses, [test_data.USER_ADDRESS])

        # Second case: get data from HDD database
        self.service.ram_db_handler.get_user_address.return_value = []
        self.service.hdd_db_handler.get_user_address.return_value = [test_data.USER_ADDRESS]
        user_addresses = self.service.get_user_address(test_data.USER_ID)
        self.assertEqual(user_addresses, [test_data.USER_ADDRESS])

        # Third case: no user data in both databases
        self.service.ram_db_handler.get_user_address.return_value = []
        self.service.hdd_db_handler.get_user_address.return_value = []
        user_addresses = self.service.get_user_address(test_data.USER_ID)
        self.assertEqual(user_addresses, [])

        # Check that internal mocked methods were called once with expected args
        self.service.hdd_db_handler.get_username.get_user_address(test_data.USER_ID)
        self.service.ram_db_handler.get_username.get_user_address(test_data.USER_ID)

    def test_check_user_id(self):
        # First case: get data from RAM database
        self.service.ram_db_handler.get_user.return_value = test_data.USER_ID
        user_id = self.service.check_user_id(test_data.USER_ID)
        self.assertEqual(user_id, test_data.USER_ID)

        # Second case: get data from HDD database
        self.service.ram_db_handler.get_user.return_value = None
        self.service.hdd_db_handler.get_user.return_value = test_data.USER_ID
        user_id = self.service.check_user_id(test_data.USER_ID)
        self.assertEqual(user_id, test_data.USER_ID)

        # Third case: no user data in both databases
        self.service.ram_db_handler.get_user.return_value = None
        self.service.hdd_db_handler.get_user.return_value = None
        user_id = self.service.check_user_id(test_data.USER_ID)
        self.assertTrue(user_id is False)

        # Check that internal mocked methods were called once with expected args
        self.service.hdd_db_handler.get_user.assert_any_call(user_id=test_data.USER_ID)
        self.service.ram_db_handler.get_user.assert_any_call(user_id=test_data.USER_ID)

    def test_user_delete(self):
        # First case: user exists in RAM database
        self.service.ram_db_handler.get_user.return_value = test_data.USER_ID
        user_deleted = self.service.delete_user(test_data.USER_ID)
        self.assertTrue(user_deleted)

        # Second case: user does exist in both databases
        self.service.ram_db_handler.get_user.return_value = None
        self.service.hdd_db_handler.get_user.return_value = None
        user_deleted = self.service.delete_user(test_data.USER_ID)
        self.assertFalse(user_deleted)

        # Check that internal mocked methods were called once with expected args
        self.service.hdd_db_handler.delete_user_messages.assert_called_once_with(test_data.USER_ID)
        self.service.hdd_db_handler.delete_user_address.assert_called_once_with(test_data.USER_ID)
        self.service.hdd_db_handler.delete_user.assert_called_once_with(user_id=test_data.USER_ID)

        self.service.ram_db_handler.delete_user_address.assert_called_once_with(test_data.USER_ID)
        self.service.hdd_db_handler.delete_user.assert_called_once_with(user_id=test_data.USER_ID)
