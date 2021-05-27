import argparse
import sys
from typing import Any, Callable, Dict, List, NamedTuple, Optional

from .base import BaseParser


class SubcommandInfo(NamedTuple):
    func: Callable[..., None]
    kwargs: Dict[str, Any]
    help_text: Optional[str]


class SubcommandParser(BaseParser):
    def __init__(
        self,
        subcommands: Dict[str, SubcommandInfo],
        no_subcommand_case: Optional[SubcommandInfo] = None,
        arg_list: List[str] = sys.argv,
        parser: Optional[argparse.ArgumentParser] = None,
    ):
        self._subcommands = subcommands
        self._no_subcommand_case = no_subcommand_case
        self._subcommand_parsers: Dict[str, argparse.ArgumentParser] = {}
        super().__init__(arg_list, parser)

    def is_no_subcommand(self) -> bool:
        return self._no_subcommand_case is not None and (
            len(self._arg_list) == 0 or self._arg_list[0] not in self._subcommands
        )

    def _add_subparsers(self):
        subparser = self._parser.add_subparsers(
            title="Subcommands",
            description=None if self._no_subcommand_case is None else "For this command, no subcommand is also possible.",
        )
        for subcommand, info in self._subcommands.items():
            if info.help_text is None:
                subcommand_parser = subparser.add_parser(subcommand)
            else:
                subcommand_parser = subparser.add_parser(subcommand, help=info.help_text)
            subcommand_parser.set_defaults(subcommand_func=info.func)
            subcommand_parser.set_defaults(subcommand_kwargs=info.kwargs)
            self._subcommand_parsers[subcommand] = subcommand_parser

    def _add_arguments(self):
        self._add_subparsers()

    def execute(self):
        if self.is_no_subcommand():
            self._no_subcommand_case.func(**self._no_subcommand_case.kwargs)
            return
        args = self._parser.parse_args(self._arg_list[:1])
        args.subcommand_func(**args.subcommand_kwargs)
