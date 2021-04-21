from azure.identity import AzureCliCredential
from azure.mgmt.cosmosdb import CosmosDBManagementClient
from azure.mgmt.cosmosdb.models import (
    BackupPolicy,
    ConsistencyPolicy,
    DatabaseAccountCreateUpdateParameters,
    Location,
)


def provision(
    credential: AzureCliCredential,
    azure_subscription_id: str,
    resource_group_name: str,
    cosmosdb_name: str,
    location: str,
    verbose: bool = True,
):
    cosmosdb_client = CosmosDBManagementClient(credential, azure_subscription_id)
    if cosmosdb_name not in {
        desc_list_res.name
        for desc_list_res in cosmosdb_client.database_accounts.list_by_resource_group(
            resource_group_name
        )
    }:
        if cosmosdb_client.database_accounts.check_name_exists(cosmosdb_name):
            if verbose:
                print(f"CosmosDB name {cosmosdb_name} is not available")
            exit(1)
        upd_params = DatabaseAccountCreateUpdateParameters(
            locations=[Location(location_name=location, failover_priority=0)],
            location=location,
            kind="GlobalDocumentDB",
            consistency_policy=ConsistencyPolicy(default_consistency_level="Session"),
            is_virtual_network_filter_enabled=False,
            enable_automatic_failover=True,
            enable_multiple_write_locations=False,
            disable_key_based_metadata_write_access=False,
            default_identity="FirstPartyIdentity",
            public_network_access="Enabled",
            enable_free_tier=True,
            enable_analytical_storage=False,
            backup_policy=BackupPolicy(type="Periodic"),
            network_acl_bypass="None",
            network_acl_bypass_resource_ids=[],
        )
        poller = cosmosdb_client.database_accounts.begin_create_or_update(
            resource_group_name, cosmosdb_name, upd_params
        )
        cosmosdb_res = poller.result()
        if verbose:
            print(f"Provisioned CosmosDB {cosmosdb_res.name}")
    else:
        if verbose:
            print(f"CosmosDB {cosmosdb_name} is already provisioned")
