import logging

logger = logging.getLogger(__name__)


def log(msg: str):
    logger.log(25, msg)
