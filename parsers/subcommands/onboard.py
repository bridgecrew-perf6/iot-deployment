import argparse
from typing import List, Optional

from parsers.base import BaseParser
from services import iot_devices


class OnboardParser(BaseParser):
    def __init__(
        self,
        arg_list: List[str],
        parser: Optional[argparse.ArgumentParser],
    ):
        super().__init__(arg_list=arg_list, parser=parser)

    def _add_arguments(self):
        self._parser.add_argument("azure_subscription_id", type=str, help="Azure subscription ID.")
        self._parser.add_argument(
            "resource_group_name",
            type=str,
            help="Resource group name for the device onboarding.",
        )
        self._parser.add_argument(
            "iot_hub_name",
            type=str,
            help="IotHub name for the device onboarding.",
        )
        self._parser.add_argument(
            "device_ids_file_path",
            type=str,
            help="Path of the text file containing 1 device id per line to be registered in IotHub.",
        )

    def execute(self):
        args = self._parser.parse_args(self._arg_list)
        logger, credential = self.get_logger_and_credential(args)
        # Step 3: Onboard & provision default IoT devices.
        iot_devices.provision(
            credential,
            args.azure_subscription_id,
            args.resource_group_name,
            args.iot_hub_name,
            args.device_ids_file_path,
            logger,
        )
