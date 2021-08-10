import argparse
from collections import OrderedDict
from typing import Any, Dict, List, Optional

from parsers.arg_defaults import (
    DEFAULT_COSMOSDB_NAME,
    DEFAULT_EVENT_HUB_NAME,
    DEFAULT_EVENT_HUB_NAMESPACE,
    DEFAULT_IIOT_APP_NAME,
    DEFAULT_IOT_HUB_NAME,
    DEFAULT_KEY_VAULT_NAME,
    DEFAULT_LOCATION,
    DEFAULT_RESOURCE_GROUP_NAME,
    DEFAULT_SERVICE_BUS_NAMESPACE,
    DEFAULT_SIGNALR_NAME,
    DEFAULT_STORAGE_ACC_NAME,
)
from parsers.base import BaseParser
from tasks import deploy_iiot


def get_arg_dictionary() -> Dict[str, Dict[str, Any]]:
    # Do not use positional arguments, to prevent possible collision with subcommand names!
    arg_dict = OrderedDict(
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
                "--storage-acc-name",
                {
                    "type": str,
                    "default": DEFAULT_STORAGE_ACC_NAME,
                    "help": "Storage account name for the deployment.",
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
                "--iiot-app-name",
                {
                    "type": str,
                    "default": DEFAULT_IIOT_APP_NAME,
                    "help": "Name of the Azure IIoT app to be registered in AAD, "
                    "as '<app_name>-client', '<app_name>-web' and '<app_name>-service'.",
                },
            ),
            (
                "--service-hostname",
                {
                    "type": str,
                    "required": True,
                    "help": "Host (domain) name where the IIoT cloud services will be available at.",
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
    return arg_dict


class IiotParser(BaseParser):
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
        deploy_iiot.task_func(args)
