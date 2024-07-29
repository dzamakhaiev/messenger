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
        user_id = self.service.create_user(self.user)
        self.assertEqual(user_id, test_data.USER_ID)
