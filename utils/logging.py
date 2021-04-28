import argparse
import logging
from logging import Logger
from typing import Dict

LOGGING_LEVEL_VAL: Dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def configure_app_logger(args: argparse.Namespace) -> Logger:
    # Configure all loggers.
    logging.basicConfig(
        format="%(asctime)s | %(levelname)s | %(name)s: %(message)s",
        datefmt="%d-%m-%Y %H:%M",
    )
    # Disable global logger.
    logging.getLogger().disabled = True
    # Configure a local logger.
    logger = logging.getLogger("iot-deployment")
    logger.setLevel(LOGGING_LEVEL_VAL[args.logging_level])
    if not args.verbose:
        logger.disabled = True

    return logger
