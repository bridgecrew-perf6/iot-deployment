import argparse
import sys

from .subcommands.deploy import DeployParser
from .subcommands.onboard import OnboardParser
from .subparser import SubcommandInfo, SubcommandParser

DEPLOY_SUBCOMMAND = "deploy"
ONBOARD_SUBCOMMAND = "onboard"


class MainParser(SubcommandParser):
    def __init__(self):
        subcommands = {
            DEPLOY_SUBCOMMAND: SubcommandInfo(self._deploy, {}, "Subcommand to deploy the Azure infrastructure."),
            ONBOARD_SUBCOMMAND: SubcommandInfo(
                self._onboard, {}, "Subcommand for batch device onboarding into the Azure IotHub."
            ),
        }
        no_subcommand_case = None
        arg_list = sys.argv[1:]
        parser = argparse.ArgumentParser()
        super().__init__(subcommands, no_subcommand_case=no_subcommand_case, arg_list=arg_list, parser=parser)

    def _deploy(self):
        deploy_parser = DeployParser(self._arg_list[1:], self._subcommand_parsers[DEPLOY_SUBCOMMAND])
        deploy_parser.execute()

    def _onboard(self):
        onboard_parser = OnboardParser(self._arg_list[1:], self._subcommand_parsers[ONBOARD_SUBCOMMAND])
        onboard_parser.execute()
