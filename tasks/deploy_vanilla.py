import argparse

from services import app_srv_plan, cosmosdb, func_apps, functions, iot_hub, resource_group, storage
from utils import get_logger_and_credential

from . import onboard


def task_func(args: argparse.Namespace):
    logger, credential = get_logger_and_credential(args)

    # Step 1: Provision the resource group.
    resource_group.provision(
        credential,
        args.azure_subscription_id,
        args.resource_group_name,
        args.location,
        logger,
    )

    # Step 2: Provision the IotHub.
    iot_hub.provision(
        credential,
        args.azure_subscription_id,
        args.resource_group_name,
        args.iot_hub_name,
        args.location,
        logger,
    )

    onboard.task_func(args)

    # Step 4: Provision the Cosmos DB and initialize it.
    cosmosdb.Provisioner(
        credential,
        args.azure_subscription_id,
        args.resource_group_name,
        args.cosmosdb_name,
        args.location,
        logger,
    ).provision()

    # Step 5: Provision an App Service Plan for Azure Functions.
    app_srv_plan.provision(
        credential,
        args.azure_subscription_id,
        args.resource_group_name,
        args.app_srv_plan_name,
        args.location,
        logger,
    )

    # Step 6: Provision a Storage account for Azure Functions.
    storage.provision(
        credential,
        args.azure_subscription_id,
        args.resource_group_name,
        args.storage_acc_name,
        args.location,
        logger,
    )

    # Step 7: Provision Azure Functions inside the ASP (app service plan).
    functions.Provisioner(
        credential,
        args.azure_subscription_id,
        args.resource_group_name,
        args.iot_hub_name,
        args.cosmosdb_name,
        args.app_srv_plan_name,
        args.storage_acc_name,
        args.functions_name,
        args.location,
        logger,
    ).provision()

    # Step 8: Initialize the Azure function apps.
    func_apps.Provisioner(
        credential,
        args.azure_subscription_id,
        args.resource_group_name,
        args.iot_hub_name,
        args.cosmosdb_name,
        args.functions_name,
        args.functions_code_path,
        args.vendor_credentials_path,
        logger,
    ).provision()
