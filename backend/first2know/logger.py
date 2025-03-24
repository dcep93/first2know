import logging

logger = logging.getLogger(__name__)


def log(src, *args):
    logger._log(25, src, *args)
