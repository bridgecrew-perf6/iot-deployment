import argparse


def add_to_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--logging-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level of the program.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="The flag for whether there should be logging messages.",
    )
