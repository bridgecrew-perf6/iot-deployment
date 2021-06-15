import argparse
from collections import OrderedDict
from typing import Any, Dict, List, Optional

from parsers.arg_defaults import (
    DEFAULT_EVENT_HUB_NAME,
    DEFAULT_EVENT_HUB_NAMESPACE,
    DEFAULT_KEY_VAULT_NAME,
    DEFAULT_LOCATION,
    DEFAULT_RESOURCE_GROUP_NAME,
    DEFAULT_SERVICE_BUS_NAMESPACE,
    DEFAULT_SIGNALR_NAME,
)
from parsers.base import BaseParser
from parsers.subcommands.subcommands.iiot import IiotParser
from parsers.subparser import SubcommandInfo, SubcommandParser
from tasks import deploy

from .subcommands import iiot, vanilla
from .subcommands.vanilla import VanillaParser

IIOT_SUBCOMMAND = "iiot"
VANILLA_SUBCOMMAND = "vanilla"


class DeployParser(SubcommandParser):
    def __init__(
        self,
        arg_list: List[str],
        parser: Optional[argparse.ArgumentParser],
    ):
        subcommands = {
            IIOT_SUBCOMMAND: SubcommandInfo(
                self._iiot,
                {},
                "Subcommand to register and deploy only Azure IIoT cloud modules into an existing kubernetes cluster "
                "(uses 'deploy-iiot.ps1').",
            ),
            VANILLA_SUBCOMMAND: SubcommandInfo(
                self._vanilla, {}, "Subcommand to deploy vanilla Azure infrastructure (without OPC UA integration)."
            ),
        }
        no_subcommand_case = SubcommandInfo(self._full_deployment, {}, None)
        super().__init__(subcommands, no_subcommand_case=no_subcommand_case, arg_list=arg_list, parser=parser)

    def _iiot(self):
        iiot_parser = IiotParser(self._arg_list[1:], self._subcommand_parsers[IIOT_SUBCOMMAND])
        iiot_parser.execute()

    def _vanilla(self):
        vanilla_parser = VanillaParser(self._arg_list[1:], self._subcommand_parsers[VANILLA_SUBCOMMAND])
        vanilla_parser.execute()

    def _full_deployment(self):
        no_subcommand_parser = NoSubcommandParser(self._arg_list, self._parser)
        no_subcommand_parser.execute()


def get_arg_dictionary() -> Dict[str, Dict[str, Any]]:
    # Do not use positional arguments, to prevent possible collision with subcommand names!
    arg_dict = vanilla.get_arg_dictionary()
    arg_dict.update(iiot.get_arg_dictionary())
    deploy_arg_dict = OrderedDict(
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
                "--tenant-id",
                {
                    "type": str,
                    "required": True,
                    "help": "The Azure Active Directory tenant ID that should be used for authenticating "
                    "requests to the key vault.",
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
                "--device-ids-file-path",
                {
                    "type": str,
                    "default": "",
                    "help": "Path of the text file containing 1 device id per line to be registered in IotHub.",
                },
            ),
            (
                "--event-hub-namespace",
                {
                    "type": str,
                    "default": DEFAULT_EVENT_HUB_NAMESPACE,
                    "help": "Name of the EventHub namespace for the deployment.",
                },
            ),
            (
                "--event-hub-name",
                {
                    "type": str,
                    "default": DEFAULT_EVENT_HUB_NAME,
                    "help": "Name of the EventHub to provision inside the EventHub namespace.",
                },
            ),
            (
                "--service-bus-namespace",
                {
                    "type": str,
                    "default": DEFAULT_SERVICE_BUS_NAMESPACE,
                    "help": "Name of the ServiceBus for the deployment.",
                },
            ),
            (
                "--key-vault-name",
                {
                    "type": str,
                    "default": DEFAULT_KEY_VAULT_NAME,
                    "help": "Name of the Key Vault for the deployment.",
                },
            ),
            (
                "--signalr-name",
                {
                    "type": str,
                    "default": DEFAULT_SIGNALR_NAME,
                    "help": "Name of the SignalR for the deployment.",
                },
            ),
            (
                "--iiot-repo-path",
                {
                    "type": str,
                    "help": "Path to the Git repository of Azure IIoT. You can clone it from "
                    "https://github.com/Azure/Industrial-IoT. If not given, then Azure IIoT modules will "
                    "not be deployed. But the required services will be deployed.",
                },
            ),
            (
                "--aad-reg-path",
                {
                    "type": str,
                    "help": "Path to the '.json' file to be created during the registration of Azure IIoT modules in AAD. "
                    "This file will also be used to deploy the modules into 'kubectl' kubernetes cluster. "
                    "If not given, then Azure IIoT modules will not be deployed. But the required services will be deployed.",
                },
            ),
            (
                "--helm-values-yaml-path",
                {
                    "type": str,
                    "help": "Path to the 'values.yaml' to be created and to be used by Helm "
                    "during the deployment of Azure IIoT cloud modules. "
                    "If not given, then Azure IIoT modules will not be deployed. But the required services will be deployed.",
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
    arg_dict.update(deploy_arg_dict)
    return arg_dict


class NoSubcommandParser(BaseParser):
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
        deploy.task_func(args)
