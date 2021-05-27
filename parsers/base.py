import abc
import argparse
import sys
from typing import List, Optional


class BaseParser(abc.ABC):
    def __init__(
        self,
        arg_list: List[str] = sys.argv,
        parser: Optional[argparse.ArgumentParser] = None,
    ):
        if parser is None:
            parser = argparse.ArgumentParser()
        self._arg_list = arg_list
        self._parser = parser
        self._add_arguments()

    @abc.abstractmethod
    def _add_arguments(self):
        raise NotImplementedError

    @abc.abstractmethod
    def execute(self):
        raise NotImplementedError
