import argparse

from utils import get_logger_and_credential

from . import deploy_vanilla


def task_func(args: argparse.Namespace):
    deploy_vanilla.task_func(args)

    # TODO: deploy OPC UA integration part.
    logger, credential = get_logger_and_credential(args)
