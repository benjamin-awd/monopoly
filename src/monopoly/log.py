import functools
import logging
import sys


def get_logger() -> logging.Logger:
    logger = logging.getLogger("root")
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    logging.getLogger("pdf2john").setLevel(logging.ERROR)
    logging.getLogger("pyhanko").setLevel(logging.ERROR)
    logging.getLogger("tzlocal").setLevel(logging.ERROR)
    return logger


def setup_logs(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs["verbose"]:
            logger = logging.getLogger("root")
            logger.setLevel(logging.DEBUG)
        result = func(*args, **kwargs)
        return result

    return wrapper
