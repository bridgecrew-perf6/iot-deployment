import base64
import json
import logging
import os
import secrets
import sys
from typing import Dict, Tuple

from azure.identity import AzureCliCredential
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import Twin
from msrest.exceptions import HttpOperationError
from utils import load_file

from services import iot_hub


class _DeviceKeys:
    def __init__(self) -> None:
        self.primary_keys = set()
        self.secondary_keys = set()
        self.id_to_keys = {}

    def generate_keys(self, device_id: str) -> Tuple[str, str]:
        # generate a unique primary key
        primary_key = base64.b64encode(secrets.token_bytes(32)).decode("utf-8")
        while primary_key in self.primary_keys:
            primary_key = base64.b64encode(secrets.token_bytes(32)).decode("utf-8")
        self.primary_keys.add(primary_key)
        # generate a unique secondary key
        secondary_key = base64.b64encode(secrets.token_bytes(32)).decode("utf-8")
        while secondary_key in self.secondary_keys:
            secondary_key = base64.b64encode(secrets.token_bytes(32)).decode("utf-8")
        self.secondary_keys.add(secondary_key)
        # Associate keys with device ids
        self.id_to_keys[device_id] = (primary_key, secondary_key)

        return primary_key, secondary_key

    def remove_device(self, device_id: str):
        primary_key, secondary_key = self.id_to_keys.pop(device_id)
        self.primary_keys.remove(primary_key)
        self.secondary_keys.remove(secondary_key)


def provision(
    credential: AzureCliCredential,
    azure_subscription_id: str,
    resource_group_name: str,
    iot_hub_name: str,
    device_ids_file_path: str,
    is_edge_device: bool,
    is_iiot_device: bool,
    logger: logging.Logger,
):
    if is_iiot_device and not is_edge_device:
        logger.error("'is_iiot_device' flag implies 'is_edge_device' which is not satisfied")
        sys.exit(1)
    device_ids = load_file.load_device_ids(device_ids_file_path)
    conn_str = iot_hub.get_connection_str(credential, azure_subscription_id, resource_group_name, iot_hub_name)
    iot_hub_reg_mgr = IoTHubRegistryManager(conn_str)

    device_keys = _DeviceKeys()
    for device_id in device_ids:
        primary_key, secondary_key = device_keys.generate_keys(device_id)
        try:
            # Import the device identity to the IotHub
            # https://docs.microsoft.com/en-us/python/api/azure-iot-hub/azure.iot.hub.iothubregistrymanager?view=azure-python#create-device-with-sas-device-id--primary-key--secondary-key--status--iot-edge-false-
            iot_hub_reg_mgr.create_device_with_sas(device_id, primary_key, secondary_key, "enabled", iot_edge=is_edge_device)
            logger.info(f"Device '{device_id}' is registered to IotHub")
        except HttpOperationError as e:
            # https://docs.microsoft.com/en-us/rest/api/iothub/common-error-codes
            if not hasattr(e.response, "status_code") or e.response.status_code != 409:
                raise e
            device_keys.remove_device(device_id)
            logger.info(f"Device '{device_id}' is already registered")
        if is_iiot_device:
            device_twin = Twin(tags={"__type__": "iiotedge", "os": "Linux"})
            iot_hub_reg_mgr.update_twin(device_id, device_twin)

    if not device_ids_file_path or not device_keys.id_to_keys:
        return
    dir_name, file_name = os.path.split(device_ids_file_path)
    id_to_keys_path = os.path.join(dir_name, f"{file_name}.keys")
    if os.path.isfile(id_to_keys_path):
        with open(id_to_keys_path, "r") as f:
            other_id_to_keys: Dict[str, Tuple[str, str]] = json.load(f)
            other_id_to_keys.update(device_keys.id_to_keys)
            device_keys.id_to_keys = other_id_to_keys
    with open(id_to_keys_path, "w") as f:
        json.dump(device_keys.id_to_keys, f, indent=2)
