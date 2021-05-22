import logging
import logging.handlers
from hcva.utils.path import create_dir


class Logger:

    def __init__(self, log_name, log_path, logger=None):
        self.logger = self.start_logger(log_name, log_path, logger)

    def get_logger(self):
        return self.logger

    # input - logName as string, logPath as string, logger as logging class
    # output - logger as logging class
    # do - set logger settings
    @staticmethod
    def start_logger(log_name, log_path, logger=None):
        path = log_path if log_path is not None else ""
        name = log_name if log_name is not None else "NoName.log"
        new_logger = logging.getLogger(log_name) if logger is None else logger
        create_dir(path)

        new_logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s: %(message)s', datefmt='%d-%m-%Y %H-%M-%S')

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        file_handler = logging.handlers.RotatingFileHandler(path + name, maxBytes=10485760, backupCount=10)
        file_handler.setFormatter(formatter)

        new_logger.addHandler(file_handler)
        new_logger.addHandler(stream_handler)

        new_logger.info('Initialize Log')
        return new_logger
