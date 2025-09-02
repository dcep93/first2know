import logging

logger = logging.getLogger(__name__)


def log(msg: str) -> None:
    logger.log(20, msg)
