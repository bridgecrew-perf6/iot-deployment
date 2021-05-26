import logging
import sys

from azure.identity import AzureCliCredential
from azure.mgmt.iothub import IotHubClient
from azure.mgmt.iothub.models import IotHubDescription, IotHubProperties, IotHubSkuInfo, OperationInputs

IOT_HUB_MGMT_API_VER = "2021-03-31"
SHARED_ACCESS_KEY_NAME = "iothubowner"
IOT_HUB_CONN_STR_TEMPLATE = "HostName={};SharedAccessKeyName={};SharedAccessKey={}"


def provision(
    credential: AzureCliCredential,
    azure_subscription_id: str,
    resource_group_name: str,
    iot_hub_name: str,
    location: str,
    logger: logging.Logger,
):
    iot_hub_client = IotHubClient(credential, azure_subscription_id, api_version=IOT_HUB_MGMT_API_VER)
    # https://docs.microsoft.com/en-us/python/api/azure-mgmt-iothub/azure.mgmt.iothub.v2020_03_01.operations.iothubresourceoperations?view=azure-python#list-by-resource-group-resource-group-name----kwargs-
    if iot_hub_name not in {
        desc_list_res.name for desc_list_res in iot_hub_client.iot_hub_resource.list_by_resource_group(resource_group_name)
    }:
        avail_res = iot_hub_client.iot_hub_resource.check_name_availability(OperationInputs(name=iot_hub_name))
        if not avail_res.name_available:
            logger.error(f"IotHub name '{iot_hub_name}' is not available")
            sys.exit(1)
        iot_hub_properties = IotHubProperties(
            public_network_access="Enabled",
            # min_tls_version="1.2",
            features="DeviceManagement",
        )
        # IotHub free: "F1", Standard: "S1"
        iot_hub_sku_info = IotHubSkuInfo(name="F1", capacity=1)
        iot_hub_desc = IotHubDescription(location=location, properties=iot_hub_properties, sku=iot_hub_sku_info)
        poller = iot_hub_client.iot_hub_resource.begin_create_or_update(resource_group_name, iot_hub_name, iot_hub_desc)
        iot_res = poller.result()
        logger.info(f"Provisioned IotHub '{iot_res.name}'")
    else:
        logger.info(f"IotHub '{iot_hub_name}' is already provisioned")


def get_connection_str(
    credential: AzureCliCredential,
    azure_subscription_id: str,
    resource_group_name: str,
    iot_hub_name: str,
) -> str:
    iot_hub_client = IotHubClient(credential, azure_subscription_id, api_version=IOT_HUB_MGMT_API_VER)
    # https://docs.microsoft.com/en-us/python/api/azure-mgmt-iothub/azure.mgmt.iothub.v2020_03_01.operations.iothubresourceoperations?view=azure-python#get-keys-for-key-name-resource-group-name--resource-name--key-name----kwargs-
    sas_auth_rule = iot_hub_client.iot_hub_resource.get_keys_for_key_name(
        resource_group_name, iot_hub_name, SHARED_ACCESS_KEY_NAME
    )
    iot_hub_desc = iot_hub_client.iot_hub_resource.get(resource_group_name, iot_hub_name)
    return IOT_HUB_CONN_STR_TEMPLATE.format(
        iot_hub_desc.properties.host_name,
        SHARED_ACCESS_KEY_NAME,
        sas_auth_rule.secondary_key,
    )
