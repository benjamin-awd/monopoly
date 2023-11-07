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
    return logger
