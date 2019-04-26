"""
Do a complete flow of input -> normalization -> segmentation -> metrics
"""

from benchmarkstt.metrics.cli import argparser as args_metrics
from benchmarkstt.metrics.cli import main as do_metrics
from benchmarkstt.normalization.cli import args_inputfile, args_logs
from benchmarkstt.normalization import NormalizationComposite, factory
from benchmarkstt.config import reader
import argparse


def argparser(parser: argparse.ArgumentParser):
    args_logs(parser)
    args_inputfile(parser)

    parser.add_argument('-c', '--config', metavar='file',
                        help='Specify config file (currently only used for loading normalization rules)')
    args_metrics(parser)
    return parser


def main(parser, args):
    normalizer = NormalizationComposite()
    rules = reader(args.config)['normalization']
    for rule in rules:
        normalizer.add(factory.create(*rule))
    do_metrics(parser, args, normalizer)
