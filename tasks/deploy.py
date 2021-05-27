import argparse

from services import event_hub
from utils import get_logger_and_credential

from . import deploy_vanilla


def task_func(args: argparse.Namespace):
    deploy_vanilla.task_func(args)

    # TODO: deploy OPC UA integration part.
    logger, credential = get_logger_and_credential(args)
    # Step 9: Provision the EventHub namespace and EventHub inside it.
    event_hub.Provisioner(
        credential,
        args.azure_subscription_id,
        args.resource_group_name,
        args.event_hub_namespace,
        args.event_hub_name,
        args.location,
        logger,
    ).provision()
