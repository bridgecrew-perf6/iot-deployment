import logging
import sys
from typing import Dict, List, Tuple

from azure.core.exceptions import ResourceExistsError
from azure.identity import AzureCliCredential
from azure.mgmt.cosmosdb import CosmosDBManagementClient
from azure.mgmt.iothub import IotHubClient
from azure.mgmt.iothub.models import EventHubProperties, IotHubProperties
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.web.models import IpSecurityRestriction, Site, SiteConfig

from services import app_srv_plan, iot_hub, storage

STORAGE_CONN_STR_TEMPLATE = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix=core.windows.net"
COSMOSDB_CONN_STR_POSTFIX = "_DOCUMENTDB"
IOT_HUB_CONN_STR_POSTFIX = "_events_IOTHUB"
COSMOSDB_CONN_STR_TEMPLATE = "AccountEndpoint={};AccountKey={};"
IOT_HUB_CONN_STR_TEMPLATE = "Endpoint={};SharedAccessKeyName={};SharedAccessKey={};EntityPath={}"
FUNCTIONS_WORKER_RUNTIME = "node"
WEBSITE_NODE_DEFAULT_VERSION = "~14"


class Provisioner:
    def __init__(
        self,
        credential: AzureCliCredential,
        azure_subscription_id: str,
        resource_group_name: str,
        iot_hub_name: str,
        cosmosdb_name: str,
        app_srv_plan_name: str,
        storage_acc_name: str,
        functions_name: str,
        location: str,
        logger: logging.Logger,
    ):
        self._credential = credential
        self._azure_subscription_id = azure_subscription_id
        self._resource_group_name = resource_group_name
        self._iot_hub_name = iot_hub_name
        self._cosmosdb_name = cosmosdb_name
        self._app_srv_plan_name = app_srv_plan_name
        self._storage_acc_name = storage_acc_name
        self._functions_name = functions_name
        self._location = location
        self._logger = logger

        self._iot_hub_client = IotHubClient(credential, azure_subscription_id, api_version=iot_hub.IOT_HUB_MGMT_API_VER)
        self._cosmosdb_client = CosmosDBManagementClient(credential, azure_subscription_id)
        self._storage_client = StorageManagementClient(
            credential, azure_subscription_id, api_version=storage.STORAGE_MGMT_API_VER
        )
        self._website_client = WebSiteManagementClient(
            credential,
            azure_subscription_id,
            api_version=app_srv_plan.WEBSITE_MGMT_API_VER,
        )

    def _get_storage_acc_key(self) -> str:
        return self._storage_client.storage_accounts.list_keys(self._resource_group_name, self._storage_acc_name).keys[1].value

    def _get_cosmosdb_uri_and_key(self) -> Tuple[str, str]:
        cosmosdb_uri = self._cosmosdb_client.database_accounts.get(
            self._resource_group_name, self._cosmosdb_name
        ).document_endpoint
        cosmosdb_key = self._cosmosdb_client.database_accounts.list_keys(
            self._resource_group_name, self._cosmosdb_name
        ).secondary_master_key
        return cosmosdb_uri, cosmosdb_key

    def _get_iot_hub_key(self) -> Tuple[EventHubProperties, str]:
        sas_auth_rule = self._iot_hub_client.iot_hub_resource.get_keys_for_key_name(
            self._resource_group_name, self._iot_hub_name, iot_hub.SHARED_ACCESS_KEY_NAME
        )
        props: IotHubProperties = self._iot_hub_client.iot_hub_resource.get(
            self._resource_group_name, self._iot_hub_name
        ).properties
        event_hub_props: EventHubProperties = props.event_hub_endpoints["events"]
        return event_hub_props, sas_auth_rule.secondary_key

    def _get_app_settings(self) -> List[Dict]:
        # Get the Storage account key.
        storage_acc_key = self._get_storage_acc_key()
        # Get the Cosmos DB uri and key.
        cosmosdb_uri, cosmosdb_key = self._get_cosmosdb_uri_and_key()
        # Get the IotHub properties and key.
        props, iot_hub_key = self._get_iot_hub_key()
        # https://docs.microsoft.com/en-us/azure/azure-functions/functions-app-settings
        return [
            {
                "name": "AzureWebJobsStorage",
                "value": STORAGE_CONN_STR_TEMPLATE.format(self._storage_acc_name, storage_acc_key),
            },
            {
                "name": "WEBSITE_CONTENTAZUREFILECONNECTIONSTRING",
                "value": STORAGE_CONN_STR_TEMPLATE.format(self._storage_acc_name, storage_acc_key),
            },
            {
                "name": f"{self._cosmosdb_name}{COSMOSDB_CONN_STR_POSTFIX}",
                "value": COSMOSDB_CONN_STR_TEMPLATE.format(cosmosdb_uri, cosmosdb_key),
            },
            {
                "name": f"{self._iot_hub_name}{IOT_HUB_CONN_STR_POSTFIX}",
                "value": IOT_HUB_CONN_STR_TEMPLATE.format(
                    props.endpoint,
                    iot_hub.SHARED_ACCESS_KEY_NAME,
                    iot_hub_key,
                    props.path,
                ),
            },
            {"name": "FUNCTIONS_EXTENSION_VERSION", "value": "~3"},
            {
                "name": "FUNCTIONS_WORKER_RUNTIME",
                "value": FUNCTIONS_WORKER_RUNTIME,
            },
            {
                "name": "WEBSITE_NODE_DEFAULT_VERSION",
                "value": WEBSITE_NODE_DEFAULT_VERSION,
            },
        ]

    def provision(self):
        if self._website_client.web_apps.get(self._resource_group_name, self._functions_name) is None:
            ip_sec = IpSecurityRestriction(
                ip_address="Any",
                action="Allow",
                priority=1,
                name="Allow all",
                description="Allow all access",
            )
            # https://docs.microsoft.com/en-us/python/api/azure-mgmt-web/azure.mgmt.web.v2020_12_01.models.siteconfig?view=azure-python
            site_conf = SiteConfig(
                app_settings=self._get_app_settings(),
                managed_pipeline_mode="Integrated",
                scm_type="LocalGit",
                load_balancing="LeastRequests",
                ip_security_restrictions=[ip_sec],
                http20_enabled=True,
                min_tls_version="1.2",
                ftps_state="FtpsOnly",
            )
            # https://docs.microsoft.com/en-us/python/api/azure-mgmt-web/azure.mgmt.web.v2020_12_01.models.site?view=azure-python
            site = Site(
                kind="functionapp",
                location=self._location,
                enabled=True,
                server_farm_id=self._website_client.app_service_plans.get(
                    self._resource_group_name, self._app_srv_plan_name
                ).id,
                reserved=False,
                site_config=site_conf,
                client_cert_mode="Required",
                https_only=True,
            )
            try:
                # https://docs.microsoft.com/en-us/python/api/azure-mgmt-web/azure.mgmt.web.v2020_12_01.operations.webappsoperations?view=azure-python#begin-create-or-update-resource-group-name--name--site-envelope----kwargs-
                poller = self._website_client.web_apps.begin_create_or_update(
                    self._resource_group_name, self._functions_name, site
                )
                func_res = poller.result()
                self._logger.info(f"Provisioned Azure Functions '{func_res.name}'")
            except ResourceExistsError as e:
                if not hasattr(e.response, "status_code") or e.response.status_code != 409:
                    raise e
                self._logger.error(f"Azure Functions name '{self._functions_name}' is not available")
                sys.exit(1)
        else:
            self._logger.info(f"Azure Functions '{self._functions_name}' is already provisioned")
