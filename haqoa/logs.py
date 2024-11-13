import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def logging_setup(logger):
    handler = RotatingFileHandler(
        'haqoa.log',
        maxBytes=1024 * 1024,  # 1MB
        backupCount=3
    )
    logger.addHandler(handler)