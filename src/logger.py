import logging
import os
from datetime import datetime


class ShellLogger:
    def __init__(self, log_file='shell.log'):
        self.log_file = log_file
        self._setup_logger()

    def _setup_logger(self):
        self.logger = logging.getLogger('pyshell')
        self.logger.setLevel(logging.INFO)

        self.logger.handlers.clear()

        formatter = logging.Formatter(
            '[%(asctime)s] - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.WARNING)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.logger.info("Python Shell started")

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)