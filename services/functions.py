from azure.core.exceptions import ResourceExistsError
from azure.identity import AzureCliCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.web.models import IpSecurityRestriction, Site, SiteConfig

from services import app_srv_plan, storage

STORAGE_CONN_STR_TEMPLATE = (
    "DefaultEndpointsProtocol=https;"
    "AccountName={};AccountKey={};EndpointSuffix=core.windows.net"
)


def provision(
    credential: AzureCliCredential,
    azure_subscription_id: str,
    resource_group_name: str,
    app_srv_plan_name: str,
    storage_acc_name: str,
    functions_name: str,
    location: str,
    verbose: bool = True,
):
    website_client = WebSiteManagementClient(
        credential, azure_subscription_id, api_version=app_srv_plan.WEBSITE_MGMT_API_VER
    )
    if website_client.web_apps.get(resource_group_name, functions_name) is None:
        # Get the Storage account key.
        storage_client = StorageManagementClient(
            credential, azure_subscription_id, api_version=storage.STORAGE_MGMT_API_VER
        )
        storage_acc_key = (
            storage_client.storage_accounts.list_keys(
                resource_group_name, storage_acc_name
            )
            .keys[1]
            .value
        )
        ip_sec = IpSecurityRestriction(
            ip_address="Any",
            action="Allow",
            priority=1,
            name="Allow all",
            description="Allow all access",
        )
        site_conf = SiteConfig(
            # https://docs.microsoft.com/en-us/azure/azure-functions/functions-app-settings
            app_settings=[
                {
                    "name": "AzureWebJobsStorage",
                    "value": STORAGE_CONN_STR_TEMPLATE.format(
                        storage_acc_name, storage_acc_key
                    ),
                },
                {
                    "name": "WEBSITE_CONTENTAZUREFILECONNECTIONSTRING",
                    "value": STORAGE_CONN_STR_TEMPLATE.format(
                        storage_acc_name, storage_acc_key
                    ),
                },
                {"name": "FUNCTIONS_EXTENSION_VERSION", "value": "~3"},
                {"name": "FUNCTIONS_WORKER_RUNTIME", "value": "node"},
                # TODO: Remove if it is useless!
                # {
                #     "name": "WEBSITE_CONTENTSHARE",
                #     "value": "functions-materialflussb780",
                # },
                {"name": "WEBSITE_NODE_DEFAULT_VERSION", "value": "~14"},
            ],
            managed_pipeline_mode="Integrated",
            load_balancing="LeastRequests",
            ip_security_restrictions=[ip_sec],
            http20_enabled=True,
            min_tls_version="1.2",
            ftps_state="FtpsOnly",
        )
        site = Site(
            kind="functionapp",
            location=location,
            enabled=True,
            server_farm_id=website_client.app_service_plans.get(
                resource_group_name, app_srv_plan_name
            ).id,
            reserved=False,
            site_config=site_conf,
            client_cert_mode="Required",
            https_only=True,
        )
        try:
            # https://docs.microsoft.com/en-us/python/api/azure-mgmt-web/azure.mgmt.web.v2020_09_01.operations.webappsoperations?view=azure-python#begin-create-or-update-resource-group-name--name--site-envelope----kwargs-
            poller = website_client.web_apps.begin_create_or_update(
                resource_group_name, functions_name, site
            )
            func_res = poller.result()
            if verbose:
                print(f"Provisioned Azure Functions '{func_res.name}'")
        except ResourceExistsError as e:
            if not hasattr(e.response, "status_code") or e.response.status_code != 409:
                raise e
            if verbose:
                print(f"Azure Functions name '{functions_name}' is not available")
    else:
        if verbose:
            print(f"Azure Functions '{functions_name}' is already provisioned")
