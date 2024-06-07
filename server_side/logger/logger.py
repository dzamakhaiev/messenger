import logging
import requests
from datetime import datetime
from server_side.logger import settings


class Logger:

    def __init__(self, logger_name, level=logging.DEBUG):
        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(level)

        formatter = logging.Formatter()

        file_handler = logging.FileHandler(f"../logs/{logger_name}.log")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(formatter)
        self.logger.addHandler(stdout_handler)

    def push_log_to_loki(self, log_row, level):
        log_json = {
            'streams': [{
                'stream': {
                    'service': self.logger_name,
                    'level': level},
                'values': [[datetime.now().strftime(settings.DATETIME_FORMAT), log_row]]}]
        }

        try:
            response = requests.post(url=settings.LOKI_URL, json=log_json)
            if response.status_code != 204:
                self.logger.error(f'Cannot push log to Loki container: {response.text}')

        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
            self.logger.critical(f'Cannot connect to Loki container: {e}')

    def error(self, msg):
        self.logger.error(msg)

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.info(msg)
