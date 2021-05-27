import argparse
from typing import List, Optional

from parsers.arg_defaults import (
    DEFAULT_APP_SRV_PLAN_NAME,
    DEFAULT_COSMOSDB_NAME,
    DEFAULT_EVENT_HUB_NAME,
    DEFAULT_EVENT_HUB_NAMESPACE,
    DEFAULT_FUNCTIONS_NAME,
    DEFAULT_IOT_HUB_NAME,
    DEFAULT_KEY_VAULT_NAME,
    DEFAULT_LOCATION,
    DEFAULT_RESOURCE_GROUP_NAME,
    DEFAULT_SERVICE_BUS_NAMESPACE,
    DEFAULT_STORAGE_ACC_NAME,
)
from parsers.base import BaseParser
from parsers.subparser import SubcommandInfo, SubcommandParser
from tasks import deploy

from .subcommands.vanilla import VanillaParser

VANILLA_SUBCOMMAND = "vanilla"


class DeployParser(SubcommandParser):
    def __init__(
        self,
        arg_list: List[str],
        parser: Optional[argparse.ArgumentParser],
    ):
        subcommands = {
            VANILLA_SUBCOMMAND: SubcommandInfo(
                self._vanilla, {}, "Subcommand to deploy vanilla Azure infrastructure (without OPC UA integration)."
            ),
        }
        no_subcommand_case = SubcommandInfo(self._full_deployment, {}, None)
        super().__init__(subcommands, no_subcommand_case=no_subcommand_case, arg_list=arg_list, parser=parser)

    def _vanilla(self):
        vanilla_parser = VanillaParser(self._arg_list[1:], self._subcommand_parsers[VANILLA_SUBCOMMAND])
        vanilla_parser.execute()

    def _full_deployment(self):
        no_subcommand_parser = NoSubcommandParser(self._arg_list, self._parser)
        no_subcommand_parser.execute()


class NoSubcommandParser(BaseParser):
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
            "--tenant-id",
            type=str,
            required=True,
            help="The Azure Active Directory tenant ID that should be used for authenticating requests to the key vault.",
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
            help="Path to the folder containing Azure Functions source code. Be warned that '.git' folder will be erased!",
        )
        self._parser.add_argument(
            "--event-hub-namespace",
            type=str,
            default=DEFAULT_EVENT_HUB_NAMESPACE,
            help="Name of the EventHub namespace for the deployment.",
        )
        self._parser.add_argument(
            "--event-hub-name",
            type=str,
            default=DEFAULT_EVENT_HUB_NAME,
            help="Name of the EventHub to provision inside the EventHub namespace.",
        )
        self._parser.add_argument(
            "--service-bus-namespace",
            type=str,
            default=DEFAULT_SERVICE_BUS_NAMESPACE,
            help="Name of the ServiceBus for the deployment.",
        )
        self._parser.add_argument(
            "--key-vault-name", type=str, default=DEFAULT_KEY_VAULT_NAME, help="Name of the Key Vault for the deployment."
        )
        self._parser.add_argument(
            "--location",
            type=str,
            default=DEFAULT_LOCATION,
            help="Location of the Azure datacenter for the deployment.",
        )

    def execute(self):
        args = self._parser.parse_args(self._arg_list)
        deploy.task_func(args)
