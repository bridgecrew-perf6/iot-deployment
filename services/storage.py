from azure.identity import AzureCliCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import (
    Sku,
    StorageAccountCheckNameAvailabilityParameters,
    StorageAccountCreateParameters,
)

STORAGE_MGMT_API_VER = "2021-02-01"


def provision(
    credential: AzureCliCredential,
    azure_subscription_id: str,
    resource_group_name: str,
    storage_acc_name: str,
    location: str,
    verbose: bool = True,
):
    storage_client = StorageManagementClient(
        credential, azure_subscription_id, api_version=STORAGE_MGMT_API_VER
    )
    if storage_acc_name not in {
        desc_list_res.name
        for desc_list_res in storage_client.storage_accounts.list_by_resource_group(
            resource_group_name
        )
    }:
        avail_res = storage_client.storage_accounts.check_name_availability(
            StorageAccountCheckNameAvailabilityParameters(name=storage_acc_name)
        )
        if not avail_res.name_available:
            if verbose:
                print(f"Storage account '{storage_acc_name}' is not available")
            exit(1)
        params = StorageAccountCreateParameters(
            sku=Sku(name="Standard_LRS"),
            kind="StorageV2",
            location=location,
            access_tier="Hot",
            enable_https_traffic_only=True,
            minimum_tls_version="TLS1_2",
        )
        # https://docs.microsoft.com/en-us/python/api/azure-mgmt-storage/azure.mgmt.storage.v2021_02_01.operations.storageaccountsoperations?view=azure-python#begin-create-resource-group-name--account-name--parameters----kwargs-
        poller = storage_client.storage_accounts.begin_create(
            resource_group_name, storage_acc_name, params
        )
        storage_res = poller.result()
        if verbose:
            print(f"Provisioned Storage account '{storage_res.name}'")
    else:
        if verbose:
            print(f"Storage account '{storage_acc_name}' is already provisioned")
