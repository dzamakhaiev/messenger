import sys
import logging


def get_logger(logger_name, level=logging.INFO):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(module)s: %(message)s")
    file_handler = logging.FileHandler(f"../logs/{logger_name}.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    return logger
