import logging
import sys

from azure.identity import AzureCliCredential
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.mgmt.keyvault.models import (
    Sku,
    VaultCheckNameAvailabilityParameters,
    VaultCreateOrUpdateParameters,
    VaultProperties,
)

KEY_VAULT_MGMT_API_VER = "2019-09-01"


def provision(
    credential: AzureCliCredential,
    azure_subscription_id: str,
    resource_group_name: str,
    key_vault_name: str,
    tenant_id: str,
    location: str,
    logger: logging.Logger,
):
    # https://docs.microsoft.com/en-us/python/api/azure-mgmt-keyvault/azure.mgmt.keyvault.v2019_09_01.operations.vaultsoperations?view=azure-python
    key_vault_client = KeyVaultManagementClient(credential, azure_subscription_id, api_version=KEY_VAULT_MGMT_API_VER)
    if key_vault_name not in {
        desc_list_res.name for desc_list_res in key_vault_client.vaults.list_by_resource_group(resource_group_name)
    }:
        avail_res = key_vault_client.vaults.check_name_availability(VaultCheckNameAvailabilityParameters(name=key_vault_name))
        if not avail_res.name_available:
            logger.error(f"Key Vault '{key_vault_name}' is not available")
            sys.exit(1)
        # https://docs.microsoft.com/en-us/python/api/azure-mgmt-keyvault/azure.mgmt.keyvault.v2019_09_01.models.sku?view=azure-python
        sb_sku = Sku(family="A", name="standard")
        kv_properties = VaultProperties(
            tenant_id=tenant_id,
            sku=sb_sku,
            access_policies=[],
            enabled_for_deployment=True,
            enabled_for_disk_encryption=True,
            enabled_for_template_deployment=True,
        )
        kv_parameters = VaultCreateOrUpdateParameters(location=location, properties=kv_properties)
        poller = key_vault_client.vaults.begin_create_or_update(resource_group_name, key_vault_name, kv_parameters)
        sb_res = poller.result()
        logger.info(f"Provisioned Key Vault '{sb_res.name}'")
    else:
        logger.info(f"Key Vault '{key_vault_name}' is already provisioned")
