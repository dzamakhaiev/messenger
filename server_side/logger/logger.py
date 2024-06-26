import os
import logging
from server_side.logger import settings


class Logger:

    def __init__(self, logger_name, level=logging.DEBUG):
        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(level)

        if os.environ.get('SERVICE_NAME') and logger_name in os.environ.get('SERVICE_NAME'):
            logger_name = os.environ.get('SERVICE_NAME')
        elif os.environ.get('SERVICE_NAME'):
            n = os.environ.get('SERVICE_NAME').split('-')[-1]
            logger_name += f'-{n}'

        formatter = logging.Formatter(settings.FORMAT)
        log_directory = os.path.abspath("../logs/")
        if not os.path.isdir(log_directory):
            os.mkdir(log_directory)
        log_file_path = os.path.join(log_directory, f"{logger_name}.log")

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(formatter)
        self.logger.addHandler(stdout_handler)

    def error(self, msg):
        self.logger.error(msg, extra={'unit': self.logger_name})

    def info(self, msg):
        self.logger.info(msg, extra={'unit': self.logger_name})

    def debug(self, msg):
        self.logger.debug(msg, extra={'unit': self.logger_name})


if __name__ == '__main__':
    logger = Logger('test')
    logger.info('Test message.')
