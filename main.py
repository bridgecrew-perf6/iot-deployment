import argparse
import random

# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from azure.identity import AzureCliCredential
from azure.mgmt.iothub import IotHubClient
from azure.mgmt.iothub.models import (
    IotHubDescription,
    IotHubProperties,
    IotHubSkuInfo,
    OperationInputs,
)
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.resource import ResourceManagementClient


RESOURCE_MGMT_API_VER = "2020-10-01"
IOT_HUB_MGMT_API_VER = "2020-03-01"
RESOURCE_ID_TEMPLATE = (
    "/subscriptions/{}/resourceGroups/{}/Microsoft.Devices/IotHubs/{}"
)
# Constants we need in multiple places: the resource group name and the region
# in which we provision resources. You can change these values however you want.
DEFAULT_RESOURCE_GROUP_NAME = "IoT-project"
DEFAULT_LOCATION = "northeurope"
DEFAULT_IOT_HUB_NAME = f"iot-hub-materialfluss{random.randint(1,100000):05}"


def main(args: argparse.Namespace):
    # Acquire a credential object using CLI-based authentication.
    credential = AzureCliCredential()

    # Obtain the management object for resources.
    resource_client = ResourceManagementClient(
        credential, args.azure_subscription_id, api_version=RESOURCE_MGMT_API_VER
    )

    # Step 1: Provision the resource group.

    if not resource_client.resource_groups.check_existence(args.resource_group_name):
        rg_result = resource_client.resource_groups.create_or_update(
            args.resource_group_name, {"location": args.location}
        )
        print(f"Provisioned resource group {rg_result.name}")
    else:
        print(f"Resource group {args.resource_group_name} is already provisioned")

    # Step 2: Provision the IotHub.

    iot_hub_client = IotHubClient(
        credential, args.azure_subscription_id, api_version=IOT_HUB_MGMT_API_VER
    )
    # https://docs.microsoft.com/en-us/azure/governance/resource-graph/reference/supported-tables-resources
    # https://docs.microsoft.com/en-us/python/api/azure-mgmt-resource/azure.mgmt.resource.resources.v2020_10_01.operations.resourcesoperations?view=azure-python#check-existence-by-id-resource-id--api-version----kwargs-
    if args.iot_hub_name not in {
        desc_list_res.name
        for desc_list_res in iot_hub_client.iot_hub_resource.list_by_resource_group(
            args.resource_group_name
        )
    }:
        avail_res = iot_hub_client.iot_hub_resource.check_name_availability(
            OperationInputs(name=args.iot_hub_name)
        )
        if not avail_res.name_available:
            print(f"IotHub name {args.iot_hub_name} is not available")
            exit(1)
        iot_hub_properties = IotHubProperties(
            public_network_access="Enabled",
            # min_tls_version="1.2",
            features="DeviceManagement",
        )
        # IotHub free: "F1", Standard: "S1"
        iot_hub_sku_info = IotHubSkuInfo(name="S1", capacity=1)
        iot_hub_desc = IotHubDescription(
            location=args.location, properties=iot_hub_properties, sku=iot_hub_sku_info
        )
        poller = iot_hub_client.iot_hub_resource.begin_create_or_update(
            args.resource_group_name, args.iot_hub_name, iot_hub_desc
        )
        iot_res = poller.result()
        print(f"Provisioned IotHub {iot_res.name}")
    else:
        print(f"IotHub{args.iot_hub_name} is already provisioned")

    # Step 3: Onboard & provision default IoT devices.


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "azure_subscription_id", type=str, help="Azure subscription ID."
    )
    parser.add_argument(
        "--resource-group-name",
        type=str,
        default=DEFAULT_RESOURCE_GROUP_NAME,
        help="Resource group name for the deployment.",
    )
    parser.add_argument(
        "--location",
        type=str,
        default=DEFAULT_LOCATION,
        help="Location of the Azure datacenter to deploy.",
    )
    parser.add_argument(
        "--iot-hub-name",
        type=str,
        default=DEFAULT_IOT_HUB_NAME,
        help="IotHub name for deployment.",
    )
    main(parser.parse_args())
