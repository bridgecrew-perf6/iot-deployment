import argparse
from typing import Optional, Tuple

from azure.identity import AzureCliCredential

from . import logging

_DEFAULT_LOGGER: Optional[logging.Logger] = None
_DEFAULT_CREDENTIAL: Optional[AzureCliCredential] = None


def get_logger_and_credential(args: argparse.Namespace) -> Tuple[logging.Logger, AzureCliCredential]:
    global _DEFAULT_LOGGER, _DEFAULT_CREDENTIAL
    if _DEFAULT_LOGGER is None:
        _DEFAULT_LOGGER = logging.configure_app_logger(args)
    if _DEFAULT_CREDENTIAL is None:
        # Acquire a credential object using CLI-based authentication.
        _DEFAULT_CREDENTIAL = AzureCliCredential()
    return _DEFAULT_LOGGER, _DEFAULT_CREDENTIAL
