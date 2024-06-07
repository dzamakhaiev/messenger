import os
import logging
import requests
from datetime import datetime
from server_side.logger import settings


class Logger:

    def __init__(self, logger_name, level=logging.DEBUG):
        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(level)

        formatter = logging.Formatter(settings.FORMAT)
        log_directory = os.path.abspath("../logs/")
        log_file_path = os.path.join(log_directory, f"{logger_name}.log")

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(formatter)
        self.logger.addHandler(stdout_handler)

    def push_log_to_loki(self, log_row, level):
        self.logger.debug('Push message to Loki container.')
        timestamp = str(int(datetime.now().timestamp() * 1e9))

        log_json = {
            'streams': [{
                'stream': {
                    'service': self.logger_name,
                    'level': level},
                'values': [[timestamp, log_row]]}]
        }

        try:
            response = requests.post(url=settings.LOKI_URL+settings.LOKI_PUSH, json=log_json)
            if response.status_code != 204:
                self.logger.error(f'Cannot push log to Loki container: {response.text}')
            else:
                self.logger.debug('Message pushed.')

        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
            self.logger.critical(f'Cannot connect to Loki container: {e}')

    def error(self, msg):
        self.logger.error(msg)
        self.push_log_to_loki(msg, 'error')

    def info(self, msg):
        self.logger.info(msg)
        self.push_log_to_loki(msg, 'info')

    def debug(self, msg):
        self.logger.debug(msg)
        self.push_log_to_loki(msg, 'debug')


if __name__ == '__main__':
    logger = Logger('test')
    logger.info('Test message.')
