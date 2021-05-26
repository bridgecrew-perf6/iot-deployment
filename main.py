import argparse
import os
import random

# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from azure.identity import AzureCliCredential

from subcommands import deploy, onboard
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


def main(subcommand_parser: argparse.ArgumentParser):
    args = subcommand_parser.parse_args()
    logger = logging.configure_app_logger(args)
    # Acquire a credential object using CLI-based authentication.
    credential = AzureCliCredential()
    args.func(args, logger, credential)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers()
    deploy_parser = subparser.add_parser("deploy", help="Subcommand to deploy the Azure infrastructure.")
    deploy_parser.add_argument("azure_subscription_id", type=str, help="Azure subscription ID.")
    deploy_parser.add_argument(
        "vendor_credentials_path",
        type=str,
        help="Path to a JSON file containing credentials for each device vendor server."
        " The JSON object must be of the following format:\n"
        '{"vendor1": {"endpoint_uri1": {"x-api-key": API_KEY}, '
        '"endpoint_uri2": {"username": USERNAME, "password": PASSWORD}}, ...}',
    )
    deploy_parser.add_argument(
        "--resource-group-name",
        type=str,
        default=DEFAULT_RESOURCE_GROUP_NAME,
        help="Resource group name for the deployment.",
    )
    deploy_parser.add_argument(
        "--iot-hub-name",
        type=str,
        default=DEFAULT_IOT_HUB_NAME,
        help="IotHub name for the deployment.",
    )
    deploy_parser.add_argument(
        "--device-ids-file-path",
        type=str,
        default="",
        help="Path of the text file containing 1 device id per line to be registered in IotHub.",
    )
    deploy_parser.add_argument(
        "--cosmosdb-name",
        type=str,
        default=DEFAULT_COSMOSDB_NAME,
        help="Cosmos DB name for the deployment.",
    )
    deploy_parser.add_argument(
        "--app-srv-plan-name",
        type=str,
        default=DEFAULT_APP_SRV_PLAN_NAME,
        help="App Service Plan name for the deployment.",
    )
    deploy_parser.add_argument(
        "--storage-acc-name",
        type=str,
        default=DEFAULT_STORAGE_ACC_NAME,
        help="Storage account name for the deployment.",
    )
    deploy_parser.add_argument(
        "--functions-name",
        type=str,
        default=DEFAULT_FUNCTIONS_NAME,
        help="Azure Functions name for the deployment.",
    )
    deploy_parser.add_argument(
        "--functions-code-path",
        type=str,
        default=DEFAULT_FUNCTIONS_CODE_PATH,
        help="Path to the folder containing Azure Functions source code." " Be warned that '.git' folder will be erased!",
    )
    deploy_parser.add_argument(
        "--location",
        type=str,
        default=DEFAULT_LOCATION,
        help="Location of the Azure datacenter to deploy.",
    )
    deploy_parser.add_argument(
        "--logging-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level of the program.",
    )
    deploy_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="The flag for whether there should be logging messages.",
    )
    deploy_parser.set_defaults(func=deploy.execute)

    onboard_parser = subparser.add_parser("onboard", help="Subcommand for batch device onboarding into the Azure IotHub.")
    onboard_parser.add_argument("azure_subscription_id", type=str, help="Azure subscription ID.")
    onboard_parser.add_argument(
        "resource_group_name",
        type=str,
        help="Resource group name for the device onboarding.",
    )
    onboard_parser.add_argument(
        "iot_hub_name",
        type=str,
        help="IotHub name for the device onboarding.",
    )
    onboard_parser.add_argument(
        "device_ids_file_path",
        type=str,
        help="Path of the text file containing 1 device id per line to be registered in IotHub.",
    )
    onboard_parser.set_defaults(func=onboard.execute)
    main(parser)
