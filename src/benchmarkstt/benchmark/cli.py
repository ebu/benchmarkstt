"""
Do a complete flow of input -> normalization -> segmentation -> metrics
"""

from benchmarkstt.metrics.cli import argparser as args_metrics
from benchmarkstt.metrics.cli import main as do_metrics
from benchmarkstt.normalization.cli import args_logs, args_normalizers, get_normalizer_from_args
import argparse


def argparser(parser: argparse.ArgumentParser):
    args_metrics(parser)
    args_normalizers(parser)
    args_logs(parser)
    return parser


def main(parser, args):
    normalizer = get_normalizer_from_args(args)
    do_metrics(parser, args, normalizer)
