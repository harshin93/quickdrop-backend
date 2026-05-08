import logging
import sys


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


gateway_logger = logging.getLogger("uvicorn.error")


def configure_logging() -> None:
    formatter = logging.Formatter(LOG_FORMAT)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    gateway_logger.handlers.clear()
    gateway_logger.addHandler(handler)
    gateway_logger.setLevel(logging.INFO)
    gateway_logger.disabled = False
    gateway_logger.propagate = False
