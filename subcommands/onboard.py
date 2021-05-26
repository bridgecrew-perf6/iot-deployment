import argparse

from azure.identity import AzureCliCredential
from services import iot_devices
from utils import logging


def execute(args: argparse.Namespace, logger: logging.Logger, credential: AzureCliCredential):
    # Step 3: Onboard & provision default IoT devices.
    iot_devices.provision(
        credential,
        args.azure_subscription_id,
        args.resource_group_name,
        args.iot_hub_name,
        args.device_ids_file_path,
        logger,
    )
