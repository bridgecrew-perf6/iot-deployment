import argparse
from typing import List, Optional

from parsers.arg_defaults import (
    DEFAULT_COSMOSDB_NAME,
    DEFAULT_EVENT_HUB_NAME,
    DEFAULT_EVENT_HUB_NAMESPACE,
    DEFAULT_IIOT_APP_NAME,
    DEFAULT_IOT_HUB_NAME,
    DEFAULT_KEY_VAULT_NAME,
    DEFAULT_RESOURCE_GROUP_NAME,
    DEFAULT_SERVICE_BUS_NAMESPACE,
    DEFAULT_SIGNALR_NAME,
    DEFAULT_STORAGE_ACC_NAME,
)
from parsers.base import BaseParser
from tasks import deploy_iiot


class IiotParser(BaseParser):
    def __init__(
        self,
        arg_list: List[str],
        parser: Optional[argparse.ArgumentParser],
    ):
        super().__init__(arg_list=arg_list, parser=parser)

    def _add_arguments(self):
        # Do not use positional arguments, to prevent possible collision with subcommand names!
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
            "--cosmosdb-name",
            type=str,
            default=DEFAULT_COSMOSDB_NAME,
            help="Cosmos DB name for the deployment.",
        )
        self._parser.add_argument(
            "--storage-acc-name",
            type=str,
            default=DEFAULT_STORAGE_ACC_NAME,
            help="Storage account name for the deployment.",
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
            "--signalr-name", type=str, default=DEFAULT_SIGNALR_NAME, help="Name of the SignalR for the deployment."
        )
        self._parser.add_argument(
            "--iiot-app-name",
            type=str,
            default=DEFAULT_IIOT_APP_NAME,
            help="Name of the Azure IIoT app to be registered in AAD, "
            "as '<app_name>-client', '<app_name>-web' and '<app_name>-service'.",
        )
        self._parser.add_argument(
            "--iiot-repo-path",
            type=str,
            required=True,
            help="Path to the Git repository of Azure IIoT. You can clone it from https://github.com/Azure/Industrial-IoT.",
        )
        self._parser.add_argument(
            "--aad-reg-path",
            type=str,
            required=True,
            help="Path to the '.json' file to be created during the registration of Azure IIoT modules in AAD. "
            "This file will also be used to deploy the modules into 'kubectl' kubernetes cluster.",
        )
        self._parser.add_argument(
            "--helm-values-yaml-path",
            type=str,
            required=True,
            help="Path to the 'values.yaml' to be created and to be used by Helm "
            "during the deployment of Azure IIoT cloud modules.",
        )

    def execute(self):
        args = self._parser.parse_args(self._arg_list)
        deploy_iiot.task_func(args)
