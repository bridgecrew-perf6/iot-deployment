import argparse

from services import event_hub, key_vault, service_bus, signalr
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
    # Step 10: Provision the ServiceBus namespace.
    service_bus.provision(
        credential,
        args.azure_subscription_id,
        args.resource_group_name,
        args.service_bus_namespace,
        args.location,
        logger,
    )
    # Step 11: Provision the Key Vault.
    key_vault.provision(
        credential,
        args.azure_subscription_id,
        args.resource_group_name,
        args.key_vault_name,
        args.tenant_id,
        args.location,
        logger,
    )
    # Step 12: Provision the SignalR.
    signalr.provision(
        credential,
        args.azure_subscription_id,
        args.resource_group_name,
        args.signalr_name,
        args.location,
        logger,
    )
