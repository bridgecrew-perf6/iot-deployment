import argparse
from collections import OrderedDict
from typing import Any, Dict, List, Optional

from parsers.base import BaseParser
from tasks import onboard


def get_arg_dictionary() -> Dict[str, Dict[str, Any]]:
    # Do not use positional arguments, to prevent possible collision with subcommand names!
    arg_dict = OrderedDict(
        [
            (
                "--azure-subscription-id",
                {
                    "type": str,
                    "required": True,
                    "help": "Azure subscription ID.",
                },
            ),
            (
                "--resource-group-name",
                {
                    "type": str,
                    "required": True,
                    "help": "Resource group name for the device onboarding.",
                },
            ),
            (
                "--iot-hub-name",
                {
                    "type": str,
                    "required": True,
                    "help": "IotHub name for the device onboarding.",
                },
            ),
            (
                "--device-ids-file-path",
                {
                    "type": str,
                    "required": True,
                    "help": "Path of the text file containing 1 device id per line to be registered in IotHub.",
                },
            ),
            (
                "--is-edge-device",
                {
                    "action": "store_true",
                    "help": "The flag for registering the devices as an iot edge device in Azure IotHub.",
                },
            ),
            (
                "--is-iiot-device",
                {
                    "action": "store_true",
                    "help": "The flag indicating whether the devices will run the Azure IIoT edge modules.",
                },
            ),
        ]
    )
    return arg_dict


class OnboardParser(BaseParser):
    def __init__(
        self,
        arg_list: List[str],
        parser: Optional[argparse.ArgumentParser],
    ):
        super().__init__(arg_list=arg_list, parser=parser)

    def _add_arguments(self):
        arg_dict = get_arg_dictionary()
        for arg, config in arg_dict.items():
            self._parser.add_argument(arg, **config)

    def execute(self):
        args = self._parser.parse_args(self._arg_list)
        onboard.task_func(args)
