import abc
import argparse
import sys
from typing import List, Optional, Tuple

from azure.identity import AzureCliCredential
from utils import logging


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

    def get_logger_and_credential(self, args: argparse.Namespace) -> Tuple[logging.Logger, AzureCliCredential]:
        logger = logging.configure_app_logger(args)
        # Acquire a credential object using CLI-based authentication.
        credential = AzureCliCredential()
        return logger, credential
