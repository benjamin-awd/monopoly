import contextvars
import functools
import logging
import sys

file_context = contextvars.ContextVar("file_context", default="N/A")
default_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
verbose_formatter = logging.Formatter("%(asctime)s - [%(file_context)s] - %(name)s - %(levelname)s - %(message)s")


class ContextFilter(logging.Filter):
    """
    Context filter that is used to inject the PDF file name into the logs.

    Only enabled in verbose mode.
    """

    def filter(self, record):
        record.file_context = file_context.get()
        return True


def set_verbose_logging():
    """Switches the logger to a more verbose format and sets the level to DEBUG."""
    logger = logging.getLogger("monopoly")
    logger.setLevel(logging.DEBUG)
    for handler in logger.handlers:
        handler.setFormatter(verbose_formatter)


def get_logger() -> logging.Logger:
    logger = logging.getLogger("monopoly")

    if logger.hasHandlers():
        return logger

    handler = logging.StreamHandler(sys.stdout)

    handler.addFilter(ContextFilter())
    handler.setFormatter(default_formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    logging.getLogger("pdf2john").setLevel(logging.ERROR)
    logging.getLogger("pyhanko").setLevel(logging.ERROR)
    logging.getLogger("tzlocal").setLevel(logging.ERROR)
    logging.getLogger("pikepdf").setLevel(logging.ERROR)
    return logger


def worker_log_setup(*, verbose: bool):
    if verbose:
        set_verbose_logging()


def setup_logs(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs.get("verbose"):
            set_verbose_logging()
        return func(*args, **kwargs)

    return wrapper
