import logging
import sys

from azure.identity import AzureCliCredential
from azure.mgmt.servicebus import ServiceBusManagementClient
from azure.mgmt.servicebus.models import CheckNameAvailability, SBNamespace, SBSku


def provision(
    credential: AzureCliCredential,
    azure_subscription_id: str,
    resource_group_name: str,
    service_bus_namespace: str,
    location: str,
    logger: logging.Logger,
):
    # https://docs.microsoft.com/en-us/python/api/azure-mgmt-servicebus/azure.mgmt.servicebus.operations.namespacesoperations?view=azure-python
    service_bus_client = ServiceBusManagementClient(credential, azure_subscription_id)
    if service_bus_namespace not in {
        desc_list_res.name for desc_list_res in service_bus_client.namespaces.list_by_resource_group(resource_group_name)
    }:
        avail_res = service_bus_client.namespaces.check_name_availability(CheckNameAvailability(name=service_bus_namespace))
        if not avail_res.name_available:
            logger.error(f"ServiceBus namespace '{service_bus_namespace}' is not available")
            sys.exit(1)
        # https://docs.microsoft.com/en-us/python/api/azure-mgmt-servicebus/azure.mgmt.servicebus.operations.namespacesoperations?view=azure-python#begin-create-or-update-resource-group-name--namespace-name--parameters----kwargs-
        sb_namespace_sku = SBSku(name="Standard", tier="Standard")
        sb_parameters = SBNamespace(location=location, sku=sb_namespace_sku, zone_redundant=False)
        poller = service_bus_client.namespaces.begin_create_or_update(
            resource_group_name, service_bus_namespace, sb_parameters
        )
        sb_res = poller.result()
        logger.info(f"Provisioned ServiceBus namespace '{sb_res.name}'")
    else:
        logger.info(f"ServiceBus namespace '{service_bus_namespace}' is already provisioned")
