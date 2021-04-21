from typing import List


def load_device_ids(device_ids_file_path: str) -> List[str]:
    device_ids = []
    if not device_ids_file_path:
        return device_ids
    with open(device_ids_file_path, "r") as f:
        device_ids = [line.strip() for line in f if line]
    return device_ids
