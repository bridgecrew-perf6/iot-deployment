import json
import logging
import os
import shutil
import stat
from typing import Dict, Optional, Tuple

from azure.identity import AzureCliCredential
from azure.mgmt.web import WebSiteManagementClient
from git import Repo

from services import app_srv_plan, cosmosdb, functions

# Make sure that there is a `TimerTrigger_<vendor_name>` Azure function for pulling
# device telemetry data from each vendor name below.
PULL_VENDOR_NAMES: Tuple[str, ...] = ("vemcon",)
assert set(PULL_VENDOR_NAMES).issubset(
    set(cosmosdb.VENDOR_NAMES)
), "pull device vendors must also be registered as vendors in cosmosdb"
COSMOS_MESSAGES_FUNC_APP_NAME = "CosmosTrigger"
IOT_HUB_EVENT_FUNC_APP_NAME = "IoTHub_EventHub"
DATA_PULLER_FUNC_APP_NAME = "TimerTrigger"
DATA_PULLER_PERIOD = "*/30 * * * * *"


class Provisioner:
    def __init__(
        self,
        credential: AzureCliCredential,
        azure_subscription_id: str,
        resource_group_name: str,
        iot_hub_name: str,
        cosmosdb_name: str,
        functions_name: str,
        functions_code_path: str,
        vendor_credentials_path: str,
        logger: logging.Logger,
    ):
        self._credential = credential
        self._azure_subscription_id = azure_subscription_id
        self._resource_group_name = resource_group_name
        self._iot_hub_name = iot_hub_name
        self._cosmosdb_name = cosmosdb_name
        self._functions_name = functions_name
        self._functions_code_path = functions_code_path
        self._vendor_credentials_path = vendor_credentials_path
        self._logger = logger

        self._repo: Optional[Repo] = None
        self._website_client = WebSiteManagementClient(
            credential,
            azure_subscription_id,
            api_version=app_srv_plan.WEBSITE_MGMT_API_VER,
        )
        self._functions_copy_path: Optional[str] = None

    def provision(self):
        if not self._functions_code_path:
            return
        self._repo_init()
        # Provision the Azure function app triggered by incoming Cosmos DB messages.
        # It will redirect these messages to the latest messages container.
        for vendor_name in cosmosdb.VENDOR_NAMES:
            self._configure_cosmos_messages_func_app(vendor_name)
        # Provision the Azure function app triggered by incoming IotHub device messages.
        # It will redirect these messages to the messages container.
        self._configure_iot_hub_event_func_app(cosmosdb.VENDOR_NAMES)
        # Provision the Azure function app triggered periodically to pull device
        # telemetry data and write it to the messages container.
        for vendor_name in PULL_VENDOR_NAMES:
            self._configure_data_puller_func_app(vendor_name)
        # Copy all the other Azure function repo files.
        self._copy_all_other()
        # Deploy all function apps
        self._repo_deploy()
        # Cleanup afterwards
        self._cleanup()
        self._logger.info("Initialized Azure function apps")

    def _code_to_copy(self, org_func_app_name: str, postfix: Optional[str] = None) -> str:
        func_app_name = org_func_app_name if postfix is None else "{}_{}".format(org_func_app_name, postfix)
        func_app_code_path = os.path.join(self._functions_code_path, org_func_app_name)
        func_app_copy_path = os.path.join(self._functions_copy_path, func_app_name)
        shutil.copytree(func_app_code_path, func_app_copy_path)
        return func_app_name

    def _repo_init(self):
        basename, dirname = os.path.split(self._functions_code_path)
        self._functions_copy_path = os.path.join(basename, f"{dirname}-copy")
        # Remove if there is a folder with the same name.
        if os.path.isdir(self._functions_copy_path):
            shutil.rmtree(self._functions_copy_path)
        # git init
        self._repo = Repo.init(self._functions_copy_path)

    def _configure_cosmos_messages_func_app(self, vendor_name: str):
        func_app_name = self._code_to_copy(COSMOS_MESSAGES_FUNC_APP_NAME, vendor_name)
        self._configure_func_app(
            func_app_name,
            {
                "bindings": [
                    {
                        "type": "cosmosDBTrigger",
                        "name": "documents",
                        "direction": "in",
                        "leaseCollectionName": cosmosdb.LEASES_CONTAINER_TEMPLATE.format(vendor_name),
                        "connectionStringSetting": "{}{}".format(self._cosmosdb_name, functions.COSMOSDB_CONN_STR_POSTFIX),
                        "databaseName": cosmosdb.COSMOSDB_DB_NAME,
                        "collectionName": vendor_name,
                        "createLeaseCollectionIfNotExists": True,
                    },
                    {
                        "name": "outputDocument",
                        "direction": "out",
                        "type": "cosmosDB",
                        "databaseName": cosmosdb.COSMOSDB_DB_NAME,
                        "collectionName": cosmosdb.LATEST_MSG_CONTAINER_TEMPLATE.format(vendor_name),
                        "connectionStringSetting": "{}{}".format(self._cosmosdb_name, functions.COSMOSDB_CONN_STR_POSTFIX),
                    },
                ]
            },
        )

    def _configure_iot_hub_event_func_app(self, vendor_names: Tuple[str, ...]):
        func_app_name = self._code_to_copy(IOT_HUB_EVENT_FUNC_APP_NAME)
        func_conf = {
            "bindings": [
                {
                    "type": "eventHubTrigger",
                    "name": "IoTHubMessages",
                    "direction": "in",
                    "eventHubName": self._iot_hub_name,
                    "connection": "{}{}".format(self._iot_hub_name, functions.IOT_HUB_CONN_STR_POSTFIX),
                    "cardinality": "many",
                    "consumerGroup": "$Default",
                },
            ]
        }
        for vendor_name in vendor_names:
            func_conf["bindings"].append(
                {
                    "name": f"outputDocument_{vendor_name}",
                    "direction": "out",
                    "type": "cosmosDB",
                    "databaseName": cosmosdb.COSMOSDB_DB_NAME,
                    "collectionName": vendor_name,
                    "connectionStringSetting": "{}{}".format(self._cosmosdb_name, functions.COSMOSDB_CONN_STR_POSTFIX),
                }
            )
        self._configure_func_app(func_app_name, func_conf)

    def _configure_data_puller_func_app(self, vendor_name: str):
        with open(self._vendor_credentials_path, "r") as f:
            all_creds = json.load(f)
        func_app_name = self._code_to_copy(f"{DATA_PULLER_FUNC_APP_NAME}_{vendor_name}")
        self._configure_func_app(
            func_app_name,
            {
                "bindings": [
                    {
                        "name": "myTimer",
                        "type": "timerTrigger",
                        "direction": "in",
                        "schedule": DATA_PULLER_PERIOD,
                    },
                    {
                        "name": "outputDocument",
                        "direction": "out",
                        "type": "cosmosDB",
                        "databaseName": cosmosdb.COSMOSDB_DB_NAME,
                        "collectionName": vendor_name,
                        "connectionStringSetting": "{}{}".format(self._cosmosdb_name, functions.COSMOSDB_CONN_STR_POSTFIX),
                    },
                ]
            },
            all_creds["vemcon"],
        )

    def _configure_func_app(self, func_app_name: str, func_conf: Dict, credentials: Optional[Dict] = None):
        func_app_path = os.path.join(self._functions_copy_path, func_app_name)
        # Configure "function.json" file.
        with open(os.path.join(func_app_path, "function.json"), "w") as f:
            json.dump(func_conf, f, indent=2, default=str)
        # If there is some credentials, write them.
        if credentials is not None:
            creds_path = os.path.join(func_app_path, "creds.json")
            with open(creds_path, "w") as f:
                json.dump(credentials, f, indent=2, default=str)

    def _copy_all_other(self):
        for item_name in os.listdir(self._functions_code_path):
            item_path = os.path.join(self._functions_code_path, item_name)
            if os.path.isfile(item_path):
                shutil.copy2(item_path, self._functions_copy_path)

    def _repo_deploy(self):
        # git add .
        self._repo.git.execute(["git", "add", "."])
        # git commit -m "initial commit"
        self._repo.git.execute(["git", "commit", "-m", "'initial commit'"])
        # Get remote git repository with credentials
        poller = self._website_client.web_apps.begin_list_publishing_credentials(
            self._resource_group_name, self._functions_name
        )
        user = poller.result()
        remote_uri = "{}/{}.git".format(user.scm_uri, self._functions_name)
        # git remote add origin <REMOTE_WITH_CREDENTIALS>
        self._repo.git.execute(["git", "remote", "add", "origin", remote_uri])
        # git push -f -u origin master
        self._repo.git.execute(["git", "push", "-f", "-u", "origin", "master"])

    def _cleanup(self):
        self._repo.close()
        for root, dirs, files in os.walk(self._functions_copy_path):
            for dir in dirs:
                os.chmod(os.path.join(root, dir), stat.S_IREAD | stat.S_IWRITE)
            for file in files:
                os.chmod(os.path.join(root, file), stat.S_IREAD | stat.S_IWRITE)
        try:
            shutil.rmtree(self._functions_copy_path)
        except OSError:
            self._logger.warning("Could not delete '{}' Please erase manually!".format(self._functions_copy_path))
