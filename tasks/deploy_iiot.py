import argparse
import os
import subprocess
import sys


def task_func(args: argparse.Namespace):
    # Step 13: Register the Azure IIoT modules to Azure AAD and deploy
    # the cloud modules into the 'kubectl' kubernetes cluster.
    if any(arg in None for arg in [args.iiot_repo_path, args.aad_reg_path, args.helm_values_yaml_path]):
        return
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
