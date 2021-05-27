import argparse
import random
from typing import List, Optional

from parsers.base import BaseParser
from tasks import deploy_vanilla

# Constants we need in multiple places: the resource group name and the region
# in which we provision resources. You can change these values however you want.
DEFAULT_RESOURCE_GROUP_NAME = "IoT-project"
DEFAULT_IOT_HUB_NAME = f"iot-hub-materialfluss{random.randint(1,100000):05}"
DEFAULT_COSMOSDB_NAME = f"cosmosdb-materialfluss{random.randint(1,100000):05}"
DEFAULT_APP_SRV_PLAN_NAME = f"ASP-materialfluss{random.randint(1,100000):05}"
DEFAULT_STORAGE_ACC_NAME = f"storage0materialfluss{random.randint(1,100000):05}"
DEFAULT_FUNCTIONS_NAME = f"functions-materialfluss{random.randint(1,100000):05}"
DEFAULT_LOCATION = "North Europe"


class VanillaParser(BaseParser):
    def __init__(
        self,
        arg_list: List[str],
        parser: Optional[argparse.ArgumentParser],
    ):
        super().__init__(arg_list=arg_list, parser=parser)

    def _add_arguments(self):
        # Do not use positional arguments, to prevent possible collision with subcommand names!
        self._parser.add_argument("--azure-subscription-id", type=str, required=True, help="Azure subscription ID.")
        self._parser.add_argument(
            "--vendor-credentials-path",
            type=str,
            required=True,
            help="Path to a JSON file containing credentials for each device vendor server."
            " The JSON object must be of the following format:\n"
            '{"vendor1": {"endpoint_uri1": {"x-api-key": API_KEY}, '
            '"endpoint_uri2": {"username": USERNAME, "password": PASSWORD}}, ...}',
        )
        self._parser.add_argument(
            "--resource-group-name",
            type=str,
            default=DEFAULT_RESOURCE_GROUP_NAME,
            help="Resource group name for the deployment.",
        )
        self._parser.add_argument(
            "--iot-hub-name",
            type=str,
            default=DEFAULT_IOT_HUB_NAME,
            help="IotHub name for the deployment.",
        )
        self._parser.add_argument(
            "--device-ids-file-path",
            type=str,
            default="",
            help="Path of the text file containing 1 device id per line to be registered in IotHub.",
        )
        self._parser.add_argument(
            "--cosmosdb-name",
            type=str,
            default=DEFAULT_COSMOSDB_NAME,
            help="Cosmos DB name for the deployment.",
        )
        self._parser.add_argument(
            "--app-srv-plan-name",
            type=str,
            default=DEFAULT_APP_SRV_PLAN_NAME,
            help="App Service Plan name for the deployment.",
        )
        self._parser.add_argument(
            "--storage-acc-name",
            type=str,
            default=DEFAULT_STORAGE_ACC_NAME,
            help="Storage account name for the deployment.",
        )
        self._parser.add_argument(
            "--functions-name",
            type=str,
            default=DEFAULT_FUNCTIONS_NAME,
            help="Azure Functions name for the deployment.",
        )
        self._parser.add_argument(
            "--functions-code-path",
            type=str,
            default="",
            help="Path to the folder containing Azure Functions source code." " Be warned that '.git' folder will be erased!",
        )
        self._parser.add_argument(
            "--location",
            type=str,
            default=DEFAULT_LOCATION,
            help="Location of the Azure datacenter to deploy.",
        )
        self._parser.add_argument(
            "--logging-level",
            type=str,
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            default="INFO",
            help="Logging level of the program.",
        )
        self._parser.add_argument(
            "--verbose",
            "-v",
            action="store_true",
            help="The flag for whether there should be logging messages.",
        )

    def execute(self):
        args = self._parser.parse_args(self._arg_list)
        deploy_vanilla.task_func(args)
