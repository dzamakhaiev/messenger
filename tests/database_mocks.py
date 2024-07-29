from unittest.mock import Mock
from tests import test_data
from server_side.database.sqlite_handler import RAMDatabaseHandler
from server_side.database.postgres_handler import PostgresHandler
from server_side.broker.mq_handler import RabbitMQHandler


def get_hdd_db_handler():
    hdd_db_handler = Mock(spec=PostgresHandler)

    # User methods
    hdd_db_handler.insert_user.return_value = None
    hdd_db_handler.get_user_id.return_value = test_data.USER_ID

    return hdd_db_handler


def get_ram_db_handler():
    ram_db_handler = Mock(spec=RAMDatabaseHandler)

    # User methods
    ram_db_handler.insert_username.return_value = None

    return ram_db_handler


def get_mq_handler():
    mq_handler = Mock(spec=RabbitMQHandler)
    return mq_handler
