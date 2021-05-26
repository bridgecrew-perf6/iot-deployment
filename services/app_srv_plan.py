import logging

from azure.identity import AzureCliCredential
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.web.models import AppServicePlan, SkuDescription

WEBSITE_MGMT_API_VER = "2020-12-01"


def provision(
    credential: AzureCliCredential,
    azure_subscription_id: str,
    resource_group_name: str,
    app_srv_plan_name: str,
    location: str,
    logger: logging.Logger,
):
    website_client = WebSiteManagementClient(credential, azure_subscription_id, api_version=WEBSITE_MGMT_API_VER)
    # https://docs.microsoft.com/en-us/python/api/azure-mgmt-web/azure.mgmt.web.v2020_09_01.operations.appserviceplansoperations?view=azure-python#list-by-resource-group-resource-group-name----kwargs-
    if app_srv_plan_name not in {
        desc_list_res.name for desc_list_res in website_client.app_service_plans.list_by_resource_group(resource_group_name)
    }:
        app_sku_info = SkuDescription(name="Y1", tier="Dynamic", size="Y1", family="Y", capacity=0)
        app_srv_plan = AppServicePlan(
            kind="functionapp",
            location=location,
            sku=app_sku_info,
            reserved=False,
        )
        poller = website_client.app_service_plans.begin_create_or_update(resource_group_name, app_srv_plan_name, app_srv_plan)
        asp_res = poller.result()
        logger.info(f"Provisioned App Service Plan '{asp_res.name}'")
    else:
        logger.info(f"App Service Plan '{app_srv_plan_name}' is already provisioned")
