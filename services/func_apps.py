import json
import logging
import os
import shutil
from typing import Dict, List, Optional

from azure.identity import AzureCliCredential
from azure.mgmt.web import WebSiteManagementClient
from git import Repo

from services import app_srv_plan, cosmosdb, functions

COSMOS_MESSAGES_FUNC_APP_NAME = "CosmosTrigger1"
IOT_HUB_EVENT_FUNC_APP_NAME = "IoTHub_EventHub1"
DATA_PULLER_FUNC_APP_NAME = "TimerTrigger1"
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
        self.credential = credential
        self.azure_subscription_id = azure_subscription_id
        self.resource_group_name = resource_group_name
        self.iot_hub_name = iot_hub_name
        self.cosmosdb_name = cosmosdb_name
        self.functions_name = functions_name
        self.functions_code_path = functions_code_path
        self.vendor_credentials_path = vendor_credentials_path
        self.logger = logger

        self.repo: Optional[Repo] = None
        self.website_client = WebSiteManagementClient(
            credential,
            azure_subscription_id,
            api_version=app_srv_plan.WEBSITE_MGMT_API_VER,
        )
        self.cleaning_list: List[str] = []

    def provision(self):
        self._repo_init()
        # Provision the Azure function app triggered by incoming CosmosDB messages.
        # It will redirect these messages to the latest messages container.
        self._configure_cosmos_messages_func_app()
        # Provision the Azure function app triggered by incoming IotHub device messages.
        # It will redirect these messages to the messages container.
        self._configure_iot_hub_event_func_app()
        # Provision the Azure function app triggered periodically to pull device
        # telemetry data and write it to the messages container.
        self._configure_data_puller_func_app()
        # Deploy all function apps
        self._repo_deploy()
        # Cleanup afterwards
        self._cleanup()
        self.logger.info("Initialized Azure function apps")

    def _configure_cosmos_messages_func_app(self):
        self._configure_func_app(
            COSMOS_MESSAGES_FUNC_APP_NAME,
            {
                "bindings": [
                    {
                        "type": "cosmosDBTrigger",
                        "name": "documents",
                        "direction": "in",
                        "leaseCollectionName": f"{cosmosdb.MSG_CONTAINER_NAME}_leases",
                        "connectionStringSetting": "{}{}".format(
                            self.cosmosdb_name, functions.COSMOSDB_CONN_STR_POSTFIX
                        ),
                        "databaseName": cosmosdb.COSMOSDB_DB_NAME,
                        "collectionName": cosmosdb.MSG_CONTAINER_NAME,
                        "createLeaseCollectionIfNotExists": True,
                    },
                    {
                        "name": "outputDocument",
                        "direction": "out",
                        "type": "cosmosDB",
                        "databaseName": cosmosdb.COSMOSDB_DB_NAME,
                        "collectionName": cosmosdb.LATEST_MSG_CONTAINER_NAME,
                        "connectionStringSetting": "{}{}".format(
                            self.cosmosdb_name, functions.COSMOSDB_CONN_STR_POSTFIX
                        ),
                    },
                ]
            },
        )

    def _configure_iot_hub_event_func_app(self):
        self._configure_func_app(
            IOT_HUB_EVENT_FUNC_APP_NAME,
            {
                "bindings": [
                    {
                        "type": "eventHubTrigger",
                        "name": "IoTHubMessages",
                        "direction": "in",
                        "eventHubName": self.iot_hub_name,
                        "connection": "{}{}".format(
                            self.iot_hub_name, functions.IOT_HUB_CONN_STR_POSTFIX
                        ),
                        "cardinality": "many",
                        "consumerGroup": "$Default",
                    },
                    {
                        "name": "outputDocument",
                        "direction": "out",
                        "type": "cosmosDB",
                        "databaseName": cosmosdb.COSMOSDB_DB_NAME,
                        "collectionName": cosmosdb.MSG_CONTAINER_NAME,
                        "connectionStringSetting": "{}{}".format(
                            self.cosmosdb_name, functions.COSMOSDB_CONN_STR_POSTFIX
                        ),
                    },
                ]
            },
        )

    def _configure_data_puller_func_app(self):
        with open(self.vendor_credentials_path, "r") as f:
            all_creds = json.load(f)
        self._configure_func_app(
            DATA_PULLER_FUNC_APP_NAME,
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
                        "collectionName": cosmosdb.MSG_CONTAINER_NAME,
                        "connectionStringSetting": "{}{}".format(
                            self.cosmosdb_name, functions.COSMOSDB_CONN_STR_POSTFIX
                        ),
                    },
                ]
            },
            all_creds["vemcon"]["api.vemcon.net"],
        )

    def _repo_init(self):
        # Remove previous .git folder, if exists.
        git_path = os.path.join(self.functions_code_path, ".git")
        if os.path.exists(git_path):
            shutil.rmtree(git_path)
        # git init
        self.repo = Repo.init(self.functions_code_path)
        self.cleaning_list.append(git_path)

    def _configure_func_app(
        self, func_app_name: str, func_conf: Dict, credentials: Optional[Dict] = None
    ):
        func_app_path = os.path.join(self.functions_code_path, func_app_name)
        # Configure "function.json" file.
        with open(os.path.join(func_app_path, "function.json"), "w") as f:
            json.dump(func_conf, f, indent=2, default=str)
        # If there is some credentials, write them.
        if credentials is not None:
            creds_path = os.path.join(func_app_path, "creds.json")
            with open(creds_path, "w") as f:
                json.dump(credentials, f, indent=2, default=str)
            self.cleaning_list.append(creds_path)

    def _repo_deploy(self):
        # git add .
        self.repo.git.execute(["git", "add", "."])
        # git commit -m "initial commit"
        self.repo.git.execute(["git", "commit", "-m", "'initial commit'"])
        # Get remote git repository with credentials
        poller = self.website_client.web_apps.begin_list_publishing_credentials(
            self.resource_group_name, self.functions_name
        )
        user = poller.result()
        remote_uri = "{}/{}.git".format(user.scm_uri, self.functions_name)
        # git remote add origin <REMOTE_WITH_CREDENTIALS>
        self.repo.git.execute(["git", "remote", "add", "origin", remote_uri])
        # git push -f -u origin master
        self.repo.git.execute(["git", "push", "-f", "-u", "origin", "master"])

    def _cleanup(self):
        for item_path in self.cleaning_list:
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except OSError:
                self.logger.warning(
                    "Could not delete '{}' Please erase manually!".format(item_path)
                )
