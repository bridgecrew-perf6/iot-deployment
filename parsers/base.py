import abc
import argparse
import sys
from typing import List, Optional

from utils import common_args


class BaseParser(abc.ABC):
    def __init__(
        self,
        arg_list: List[str] = sys.argv,
        parser: Optional[argparse.ArgumentParser] = None,
        add_common_args: bool = True,
    ):
        if parser is None:
            parser = argparse.ArgumentParser()
        self._arg_list = arg_list
        self._parser = parser
        self._add_arguments()
        if add_common_args:
            common_args.add_to_parser(self._parser)

    @abc.abstractmethod
    def _add_arguments(self):
        raise NotImplementedError

    @abc.abstractmethod
    def execute(self):
        raise NotImplementedError
