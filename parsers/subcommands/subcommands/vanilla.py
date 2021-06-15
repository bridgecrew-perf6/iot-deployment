import argparse
from collections import OrderedDict
from typing import Any, Dict, List, Optional

from parsers.arg_defaults import (
    DEFAULT_APP_SRV_PLAN_NAME,
    DEFAULT_COSMOSDB_NAME,
    DEFAULT_FUNCTIONS_NAME,
    DEFAULT_IOT_HUB_NAME,
    DEFAULT_LOCATION,
    DEFAULT_RESOURCE_GROUP_NAME,
    DEFAULT_STORAGE_ACC_NAME,
)
from parsers.base import BaseParser
from tasks import deploy_vanilla

from .. import onboard


def get_arg_dictionary() -> Dict[str, Dict[str, Any]]:
    # Do not use positional arguments, to prevent possible collision with subcommand names!
    arg_dict = onboard.get_arg_dictionary()
    vanilla_arg_dict = OrderedDict(
        [
            (
                "--azure-subscription-id",
                {
                    "type": str,
                    "required": True,
                    "help": "Azure subscription ID.",
                },
            ),
            (
                "--vendor-credentials-path",
                {
                    "type": str,
                    "required": True,
                    "help": "Path to a JSON file containing credentials for each device vendor server."
                    " The JSON object must be of the following format:\n"
                    '{"vendor1": {"endpoint_uri1": {"x-api-key": API_KEY}, '
                    '"endpoint_uri2": {"username": USERNAME, "password": PASSWORD}}, ...}',
                },
            ),
            (
                "--resource-group-name",
                {
                    "type": str,
                    "default": DEFAULT_RESOURCE_GROUP_NAME,
                    "help": "Resource group name for the deployment.",
                },
            ),
            (
                "--iot-hub-name",
                {
                    "type": str,
                    "default": DEFAULT_IOT_HUB_NAME,
                    "help": "IotHub name for the deployment.",
                },
            ),
            (
                "--cosmosdb-name",
                {
                    "type": str,
                    "default": DEFAULT_COSMOSDB_NAME,
                    "help": "Cosmos DB name for the deployment.",
                },
            ),
            (
                "--app-srv-plan-name",
                {
                    "type": str,
                    "default": DEFAULT_APP_SRV_PLAN_NAME,
                    "help": "App Service Plan name for the deployment.",
                },
            ),
            (
                "--storage-acc-name",
                {
                    "type": str,
                    "default": DEFAULT_STORAGE_ACC_NAME,
                    "help": "Storage account name for the deployment.",
                },
            ),
            (
                "--functions-name",
                {
                    "type": str,
                    "default": DEFAULT_FUNCTIONS_NAME,
                    "help": "Azure Functions name for the deployment.",
                },
            ),
            (
                "--functions-code-path",
                {
                    "type": str,
                    "default": "",
                    "help": "Path to the folder containing Azure Functions source code. Be warned that "
                    "'.git' folder will be erased!",
                },
            ),
            (
                "--location",
                {
                    "type": str,
                    "default": DEFAULT_LOCATION,
                    "help": "Location of the Azure datacenter for the deployment.",
                },
            ),
        ]
    )
    arg_dict.update(vanilla_arg_dict)
    return arg_dict


class VanillaParser(BaseParser):
    def __init__(
        self,
        arg_list: List[str],
        parser: Optional[argparse.ArgumentParser],
    ):
        super().__init__(arg_list=arg_list, parser=parser)

    def _add_arguments(self):
        arg_dict = get_arg_dictionary()
        for arg, config in arg_dict.items():
            self._parser.add_argument(arg, **config)

    def execute(self):
        args = self._parser.parse_args(self._arg_list)
        deploy_vanilla.task_func(args)
