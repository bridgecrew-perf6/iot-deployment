import argparse

from services import iot_devices
from utils import get_logger_and_credential


def task_func(args: argparse.Namespace):
    logger, credential = get_logger_and_credential(args)

    # Step 3: Onboard & provision default IoT devices.
    iot_devices.provision(
        credential,
        args.azure_subscription_id,
        args.resource_group_name,
        args.iot_hub_name,
        args.device_ids_file_path,
        args.is_edge_device,
        args.is_iiot_device,
        logger,
    )
