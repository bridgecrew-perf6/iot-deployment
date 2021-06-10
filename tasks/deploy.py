import argparse
import os
import subprocess
import sys

from services import event_hub, key_vault, service_bus, signalr
from utils import get_logger_and_credential

from . import deploy_vanilla


def task_func(args: argparse.Namespace):
    deploy_vanilla.task_func(args)

    # TODO: deploy OPC UA integration part.
    logger, credential = get_logger_and_credential(args)
    # Step 9: Provision the EventHub namespace and EventHub inside it.
    event_hub.Provisioner(
        credential,
        args.azure_subscription_id,
        args.resource_group_name,
        args.event_hub_namespace,
        args.event_hub_name,
        args.location,
        logger,
    ).provision()
    # Step 10: Provision the ServiceBus namespace.
    service_bus.provision(
        credential,
        args.azure_subscription_id,
        args.resource_group_name,
        args.service_bus_namespace,
        args.location,
        logger,
    )
    # Step 11: Provision the Key Vault.
    key_vault.provision(
        credential,
        args.azure_subscription_id,
        args.resource_group_name,
        args.key_vault_name,
        args.tenant_id,
        args.location,
        logger,
    )
    # Step 12: Provision the SignalR.
    signalr.provision(
        credential,
        args.azure_subscription_id,
        args.resource_group_name,
        args.signalr_name,
        args.location,
        logger,
    )
    # Step 13: Register the Azure IIoT modules to Azure AAD and deploy
    # the cloud modules into the 'kubectl' kubernetes cluster.
    p = subprocess.Popen(
        [
            "powershell",
            os.path.join(".", "scripts", "deploy-iiot.ps1"),
            "-RGName",
            args.resource_group_name,
            "-IotHubName",
            args.iot_hub_name,
            "-CosmosDBName",
            args.cosmosdb_name,
            "-StorageAccName",
            args.storage_acc_name,
            "-EvHubNamespace",
            args.event_hub_namespace,
            "-EvHubName",
            args.event_hub_name,
            "-SerBusNamespace",
            args.service_bus_namespace,
            "-KeyVaultName",
            args.key_vault_name,
            "-SignalRName",
            args.signalr_name,
            "-IIoTAppName",
            args.iiot_app_name,
            "-IIoTRepoPath",
            args.iiot_repo_path,
            "-AadRegPath",
            args.aad_reg_path,
            "-ValuesYamlPath",
            args.helm_values_yaml_path,
        ],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    p.communicate()
