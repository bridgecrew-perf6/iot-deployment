from azure.identity import AzureCliCredential
from azure.mgmt.iothub import IotHubClient
from azure.mgmt.iothub.models import (
    IotHubDescription,
    IotHubProperties,
    IotHubSkuInfo,
    OperationInputs,
)

IOT_HUB_MGMT_API_VER = "2020-03-01"


def provision(
    credential: AzureCliCredential,
    azure_subscription_id: str,
    resource_group_name: str,
    iot_hub_name: str,
    location: str,
    verbose: bool = True,
):
    iot_hub_client = IotHubClient(
        credential, azure_subscription_id, api_version=IOT_HUB_MGMT_API_VER
    )
    # https://docs.microsoft.com/en-us/azure/governance/resource-graph/reference/supported-tables-resources
    # https://docs.microsoft.com/en-us/python/api/azure-mgmt-resource/azure.mgmt.resource.resources.v2020_10_01.operations.resourcesoperations?view=azure-python#check-existence-by-id-resource-id--api-version----kwargs-
    if iot_hub_name not in {
        desc_list_res.name
        for desc_list_res in iot_hub_client.iot_hub_resource.list_by_resource_group(
            resource_group_name
        )
    }:
        avail_res = iot_hub_client.iot_hub_resource.check_name_availability(
            OperationInputs(name=iot_hub_name)
        )
        if not avail_res.name_available:
            if verbose:
                print(f"IotHub name {iot_hub_name} is not available")
            exit(1)
        iot_hub_properties = IotHubProperties(
            public_network_access="Enabled",
            # min_tls_version="1.2",
            features="DeviceManagement",
        )
        # IotHub free: "F1", Standard: "S1"
        iot_hub_sku_info = IotHubSkuInfo(name="S1", capacity=1)
        iot_hub_desc = IotHubDescription(
            location=location, properties=iot_hub_properties, sku=iot_hub_sku_info
        )
        poller = iot_hub_client.iot_hub_resource.begin_create_or_update(
            resource_group_name, iot_hub_name, iot_hub_desc
        )
        iot_res = poller.result()
        if verbose:
            print(f"Provisioned IotHub {iot_res.name}")
    else:
        if verbose:
            print(f"IotHub{iot_hub_name} is already provisioned")
