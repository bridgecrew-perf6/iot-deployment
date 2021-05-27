import logging
import sys

from azure.identity import AzureCliCredential
from azure.mgmt.eventhub import EventHubManagementClient
from azure.mgmt.eventhub.models import CheckNameAvailabilityParameter, EHNamespace, Eventhub, NetworkRuleSet, Sku

EVENT_HUB_MGMT_API_VER = "2017-04-01"


class Provisioner:
    def __init__(
        self,
        credential: AzureCliCredential,
        azure_subscription_id: str,
        resource_group_name: str,
        event_hub_namespace: str,
        event_hub_name: str,
        location: str,
        logger: logging.Logger,
    ):
        self._credential = credential
        self._azure_subscription_id = azure_subscription_id
        self._resource_group_name = resource_group_name
        self._event_hub_namespace = event_hub_namespace
        self._event_hub_name = event_hub_name
        self._location = location
        self._logger = logger

        self._event_hub_client = EventHubManagementClient(
            credential, azure_subscription_id, api_version=EVENT_HUB_MGMT_API_VER
        )

    def _provision_eh_namespace(self):
        # https://docs.microsoft.com/en-us/python/api/azure-mgmt-eventhub/azure.mgmt.eventhub.v2017_04_01.operations.namespacesoperations?view=azure-python
        if self._event_hub_namespace not in {
            desc_list_res.name
            for desc_list_res in self._event_hub_client.namespaces.list_by_resource_group(self._resource_group_name)
        }:
            avail_res = self._event_hub_client.namespaces.check_name_availability(
                CheckNameAvailabilityParameter(name=self._event_hub_namespace)
            )
            if not avail_res.name_available:
                self._logger.error(f"EventHub namespace '{self._event_hub_namespace}' is not available")
                sys.exit(1)
            # https://docs.microsoft.com/en-us/python/api/azure-mgmt-eventhub/azure.mgmt.eventhub.v2017_04_01.models.ehnamespace?view=azure-python
            eh_namespace_sku = Sku(name="Standard", tier="Standard", capacity=1)
            # https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-auto-inflate
            eh_namespace = EHNamespace(
                location=self._location, sku=eh_namespace_sku, is_auto_inflate_enabled=True, maximum_throughput_units=20
            )
            poller = self._event_hub_client.namespaces.begin_create_or_update(
                self._resource_group_name, self._event_hub_namespace, eh_namespace
            )
            eh_res = poller.result()
            net_ruleset = NetworkRuleSet(default_action="Allow")
            self._event_hub_client.namespaces.create_or_update_network_rule_set(
                self._resource_group_name, self._event_hub_namespace, net_ruleset
            )
            self._logger.info(f"Provisioned EventHub namespace '{eh_res.name}'")
        else:
            self._logger.info(f"EventHub namespace '{self._event_hub_namespace}' is already provisioned")

    def _provision_eh(self):
        # https://docs.microsoft.com/en-us/python/api/azure-mgmt-eventhub/azure.mgmt.eventhub.v2017_04_01.operations.eventhubsoperations?view=azure-python#methods
        if self._event_hub_name not in {
            desc_list_res.name
            for desc_list_res in self._event_hub_client.event_hubs.list_by_namespace(
                self._resource_group_name, self._event_hub_namespace
            )
        }:
            # https://docs.microsoft.com/en-us/python/api/azure-mgmt-eventhub/azure.mgmt.eventhub.v2017_04_01.operations.eventhubsoperations?view=azure-python#create-or-update-resource-group-name--namespace-name--event-hub-name--parameters----kwargs-
            # https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-faq#partitions
            eh_parameters = Eventhub(message_retention_in_days=1, partition_count=32)
            eh = self._event_hub_client.event_hubs.create_or_update(
                self._resource_group_name, self._event_hub_namespace, self._event_hub_name, eh_parameters
            )
            self._logger.info(f"Provisioned EventHub '{eh.name}'")
        else:
            self._logger.info(f"EventHub '{self._event_hub_name}' is already provisioned")

    def provision(self):
        # Provision the EventHub namespace first.
        self._provision_eh_namespace()
        # Provision the EventHub inside the EventHub namespace.
        self._provision_eh()
