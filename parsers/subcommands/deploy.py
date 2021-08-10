import argparse
from typing import Any, Dict, List, Optional

from parsers.base import BaseParser
from parsers.subcommands.subcommands.iiot import IiotParser
from parsers.subparser import SubcommandInfo, SubcommandParser
from tasks import deploy

from .subcommands import iiot, vanilla
from .subcommands.vanilla import VanillaParser

IIOT_SUBCOMMAND = "iiot"
VANILLA_SUBCOMMAND = "vanilla"


class DeployParser(SubcommandParser):
    def __init__(
        self,
        arg_list: List[str],
        parser: Optional[argparse.ArgumentParser],
    ):
        subcommands = {
            IIOT_SUBCOMMAND: SubcommandInfo(
                self._iiot,
                {},
                "Subcommand to register and deploy only Azure IIoT cloud modules into an existing kubernetes cluster "
                "(uses 'deploy-iiot.ps1').",
            ),
            VANILLA_SUBCOMMAND: SubcommandInfo(
                self._vanilla, {}, "Subcommand to deploy vanilla Azure infrastructure (without OPC UA integration)."
            ),
        }
        no_subcommand_case = SubcommandInfo(self._full_deployment, {}, None)
        super().__init__(subcommands, no_subcommand_case=no_subcommand_case, arg_list=arg_list, parser=parser)

    def _iiot(self):
        iiot_parser = IiotParser(self._arg_list[1:], self._subcommand_parsers[IIOT_SUBCOMMAND])
        iiot_parser.execute()

    def _vanilla(self):
        vanilla_parser = VanillaParser(self._arg_list[1:], self._subcommand_parsers[VANILLA_SUBCOMMAND])
        vanilla_parser.execute()

    def _full_deployment(self):
        no_subcommand_parser = NoSubcommandParser(self._arg_list, self._parser)
        no_subcommand_parser.execute()


def get_arg_dictionary() -> Dict[str, Dict[str, Any]]:
    # Do not use positional arguments, to prevent possible collision with subcommand names!
    arg_dict = vanilla.get_arg_dictionary()
    arg_dict.update(iiot.get_arg_dictionary())
    return arg_dict


class NoSubcommandParser(BaseParser):
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
        deploy.task_func(args)
