from loguru import logger
# from creator.config.library import config


class LoggerFile:
    def __init__(self, level='INFO'):
        """
        Initialize a new logger file.

        Args:
            level (str, optional): Logging level. Defaults to 'INFO'.
        """
        self.level = level
        logger.remove()
        logger.add("output.log", format="{message}")  # Adjust as needed

    def write(self, data):
        """
        Write data to the logger.

        Args:
            data (str): The data to write.
        """
        logger.log(self.level, data)

    def flush(self):
        """
        Flush the logger. This is a no-op since loguru handles flushing automatically.
        """
        pass


logger_file = LoggerFile()
