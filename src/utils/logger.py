import logging

class LoggerSingleton:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            logging.basicConfig(level=logging.INFO)
            cls._instance.logger = logging.getLogger('ci-sync')
        return cls._instance

    def info(self, msg): self.logger.info(msg)
    def error(self, msg): self.logger.error(msg)
