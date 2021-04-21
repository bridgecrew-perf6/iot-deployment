from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient

RESOURCE_MGMT_API_VER = "2020-10-01"


def provision(
    credential: AzureCliCredential,
    azure_subscription_id: str,
    resource_group_name: str,
    location: str,
    verbose: bool = True,
):
    resource_client = ResourceManagementClient(
        credential, azure_subscription_id, api_version=RESOURCE_MGMT_API_VER
    )
    if not resource_client.resource_groups.check_existence(resource_group_name):
        rg_result = resource_client.resource_groups.create_or_update(
            resource_group_name, {"location": location}
        )
        if verbose:
            print(f"Provisioned resource group {rg_result.name}")
    else:
        if verbose:
            print(f"Resource group {resource_group_name} is already provisioned")
