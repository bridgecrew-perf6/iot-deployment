import argparse

from azure.identity import AzureCliCredential
from services import app_srv_plan, cosmosdb, func_apps, functions, iot_devices, iot_hub, resource_group, storage
from utils import logging


def execute(args: argparse.Namespace, logger: logging.Logger, credential: AzureCliCredential):
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

    # Step 3: Onboard & provision default IoT devices.
    iot_devices.provision(
        credential,
        args.azure_subscription_id,
        args.resource_group_name,
        args.iot_hub_name,
        args.device_ids_file_path,
        logger,
    )

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
