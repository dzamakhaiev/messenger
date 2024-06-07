import logging


class Logger:

    def __init__(self, logger_name, level=logging.DEBUG):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(level)

        formatter = logging.Formatter("%(asctime)s %(levelname)s %(module)s: %(message)s")

        file_handler = logging.FileHandler(f"../logs/{logger_name}.log")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(formatter)
        self.logger.addHandler(stdout_handler)

    def error(self, msg):
        self.logger.error(msg)

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.info(msg)
