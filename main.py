import argparse
import os
import random

# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from azure.identity import AzureCliCredential

from services import app_srv_plan, cosmosdb, func_apps, functions, iot_devices, iot_hub, resource_group, storage
from utils import logging

# Constants we need in multiple places: the resource group name and the region
# in which we provision resources. You can change these values however you want.
DEFAULT_RESOURCE_GROUP_NAME = "IoT-project"
DEFAULT_IOT_HUB_NAME = f"iot-hub-materialfluss{random.randint(1,100000):05}"
DEFAULT_COSMOSDB_NAME = f"cosmosdb-materialfluss{random.randint(1,100000):05}"
DEFAULT_APP_SRV_PLAN_NAME = f"ASP-materialfluss{random.randint(1,100000):05}"
DEFAULT_STORAGE_ACC_NAME = f"storage0materialfluss{random.randint(1,100000):05}"
DEFAULT_FUNCTIONS_NAME = f"functions-materialfluss{random.randint(1,100000):05}"
DEFAULT_FUNCTIONS_CODE_PATH = os.path.join(".", "functions-code")
DEFAULT_LOCATION = "North Europe"


def main(args: argparse.Namespace):
    logger = logging.configure_app_logger(args)

    # Acquire a credential object using CLI-based authentication.
    credential = AzureCliCredential()

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

    # Step 4: Provision the CosmosDB and initialize it.
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("azure_subscription_id", type=str, help="Azure subscription ID.")
    parser.add_argument(
        "vendor_credentials_path",
        type=str,
        help="Path to a JSON file containing credentials for each device vendor server."
        " The JSON object must be of the following format:\n"
        '{"vendor1": {"endpoint_uri1": {"x-api-key": API_KEY}, '
        '"endpoint_uri2": {"username": USERNAME, "password": PASSWORD}}, ...}',
    )
    parser.add_argument(
        "--resource-group-name",
        type=str,
        default=DEFAULT_RESOURCE_GROUP_NAME,
        help="Resource group name for the deployment.",
    )
    parser.add_argument(
        "--iot-hub-name",
        type=str,
        default=DEFAULT_IOT_HUB_NAME,
        help="IotHub name for deployment.",
    )
    parser.add_argument(
        "--device-ids-file-path",
        type=str,
        default="",
        help="Path of the text file containing 1 " "device id per line to be registered in IotHub.",
    )
    parser.add_argument(
        "--cosmosdb-name",
        type=str,
        default=DEFAULT_COSMOSDB_NAME,
        help="CosmosDB name for the deployment.",
    )
    parser.add_argument(
        "--app-srv-plan-name",
        type=str,
        default=DEFAULT_APP_SRV_PLAN_NAME,
        help="App Service Plan name for the deployment.",
    )
    parser.add_argument(
        "--storage-acc-name",
        type=str,
        default=DEFAULT_STORAGE_ACC_NAME,
        help="Storage account name for the deployment.",
    )
    parser.add_argument(
        "--functions-name",
        type=str,
        default=DEFAULT_FUNCTIONS_NAME,
        help="Azure Functions name for the deployment.",
    )
    parser.add_argument(
        "--functions-code-path",
        type=str,
        default=DEFAULT_FUNCTIONS_CODE_PATH,
        help="Path to the folder containing Azure Functions source code." " Be warned that '.git' folder will be erased!",
    )
    parser.add_argument(
        "--location",
        type=str,
        default=DEFAULT_LOCATION,
        help="Location of the Azure datacenter to deploy.",
    )
    parser.add_argument(
        "--logging-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level of the program.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="The flag for whether there should be logging messages.",
    )
    main(parser.parse_args())
