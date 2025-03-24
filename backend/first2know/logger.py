import logging

logger = logging.getLogger(__name__)


def log(src: str, *args):
    logger._log(25, src, args)
