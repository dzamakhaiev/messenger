from unittest.mock import Mock
from server_side.database.sqlite_handler import RAMDatabaseHandler
from server_side.database.postgres_handler import PostgresHandler
from server_side.broker.mq_handler import RabbitMQHandler


def get_hdd_db_handler() -> Mock:
    hdd_db_handler = Mock(spec=PostgresHandler)
    return hdd_db_handler


def get_ram_db_handler() -> Mock:
    ram_db_handler = Mock(spec=RAMDatabaseHandler)
    return ram_db_handler


def get_mq_handler() -> Mock:
    mq_handler = Mock(spec=RabbitMQHandler)
    return mq_handler
