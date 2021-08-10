import argparse

from . import deploy_iiot, deploy_vanilla


def task_func(args: argparse.Namespace):
    deploy_vanilla.task_func(args)
    deploy_iiot.task_func(args)
