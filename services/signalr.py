import logging
import sys

from azure.identity import AzureCliCredential
from azure.mgmt.signalr import SignalRManagementClient
from azure.mgmt.signalr.models import ResourceSku, SignalRFeature, SignalRNetworkACLs, SignalRResource
from utils.identity import AzureIdentityCredentialAdapter


def provision(
    credential: AzureCliCredential,
    azure_subscription_id: str,
    resource_group_name: str,
    signalr_name: str,
    location: str,
    logger: logging.Logger,
):
    # https://azuresdkdocs.blob.core.windows.net/$web/python/azure-mgmt-signalr/1.0.0b2/azure.mgmt.signalr.operations.html#azure.mgmt.signalr.operations.SignalROperations
    signalr_client = SignalRManagementClient(AzureIdentityCredentialAdapter(credential), azure_subscription_id)
    if signalr_name not in {
        desc_list_res.name for desc_list_res in signalr_client.signal_r.list_by_resource_group(resource_group_name)
    }:
        avail_res = signalr_client.signal_r.check_name_availability(
            location, "Microsoft.SignalRService/SignalR", name=signalr_name
        )
        if not avail_res.name_available:
            logger.error(f"SignalR '{signalr_name}' is not available")
            sys.exit(1)
        # https://azuresdkdocs.blob.core.windows.net/$web/python/azure-mgmt-signalr/1.0.0b2/azure.mgmt.signalr.models.html#azure.mgmt.signalr.models.ResourceSku
        sr_sku = ResourceSku(name="Free_F1", tier="Free", capacity=1)
        sr_parameters = SignalRResource(
            location=location,
            sku=sr_sku,
            kind="SignalR",
            features=[SignalRFeature(flag="ServiceMode", value="Default")],
            network_ac_ls=SignalRNetworkACLs(default_action="Allow"),
        )
        poller = signalr_client.signal_r.create_or_update(resource_group_name, signalr_name, sr_parameters)
        sr_res = poller.result()
        logger.info(f"Provisioned SignalR '{sr_res.name}'")
    else:
        logger.info(f"SignalR '{signalr_name}' is already provisioned")
