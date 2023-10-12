import os
from loguru import logger
from creator.config.library import config
from datetime import datetime
import time


class LoggerFile:
    def __init__(self, log_path, level='INFO'):
        """
        Initialize a new logger file.

        Args:
            level (str, optional): Logging level. Defaults to 'INFO'.
        """
        self.level = level
        logger.remove()
        self.last_write_time = time.time()
        self.log_path = log_path
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        log_file_path = os.path.join(os.path.dirname(log_path), f"output{timestamp}.log")
        logger.add(log_file_path, format="{message}")  # Adjust as needed

    def check_and_rotate_log(self):
        """
        Check the last write time and rotate the log file if needed.
        """
        if time.time() - self.last_write_time > 5 * 60:  # 5 minutes
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            new_log_path = os.path.join(os.path.dirname(self.log_path), f"output{timestamp}.log")
            logger.remove()
            logger.add(new_log_path, format="{message}")
            self.log_path = new_log_path
            self.last_write_time = time.time()

    def write(self, data):
        """
        Write data to the logger and update the last write time.
        """
        self.check_and_rotate_log()
        logger.log(self.level, data)
        self.last_write_time = time.time()

    def flush(self):
        """
        Flush the logger. This is a no-op since loguru handles flushing automatically.
        """
        pass


logger_file = LoggerFile(log_path=os.path.join(config.logger_cache_path))
