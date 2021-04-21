from typing import List


def load_device_ids(device_ids_file_path: str) -> List[str]:
    device_ids = []
    with open(device_ids_file_path, "r") as f:
        for line in f:
            if line != "":
                device_ids.append(line.strip())
    return device_ids
