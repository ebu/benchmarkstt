"""
Do a complete flow of input -> normalization -> segmentation -> metrics
"""

import benchmarkstt.cli.entrypoints.metrics as metrics_cli
from benchmarkstt.cli.entrypoints.normalization import args_logs, args_normalizers, get_normalizer_from_args
import argparse

# hidden: don't add this as a subcommand to benchmarkstt-tools
hidden = True


def argparser(parser: argparse.ArgumentParser):
    metrics_cli.argparser(parser)
    args_normalizers(parser)
    args_logs(parser)
    return parser


def run(parser, args):
    normalizer = get_normalizer_from_args(args)
    metrics_cli.run(parser, args, normalizer)
