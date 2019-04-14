from benchmarkstt.metrics.core import WER, WordDiffs, DiffCounts
from benchmarkstt.input import core
from benchmarkstt.metrics import factory
from benchmarkstt.cli import args_from_factory
import argparse


def argparser(parser: argparse.ArgumentParser):
    # steps: input normalize[pre?] segmentation normalize[post?] compare
    parser.add_argument('-r', '--reference', required=True,
                        help='The file to use as reference')
    parser.add_argument('-h', '--hypothesis', required=True,
                        help='The file to use as hypothesis')

    parser.add_argument('-rt', '--reference-type', default='infer',
                        help='Type of reference file')
    parser.add_argument('-ht', '--hypothesis-type', default='infer',
                        help='Type of hypothesis file')

    # parser.add_argument('-m', '--metric', default='wer', nargs='+',
    #                     help='The type of metric(s) to run')

    metrics_desc = " A list of metrics to calculate. At least one metric needs to be provided."

    subparser = parser.add_argument_group('available metrics', description=metrics_desc)
    args_from_factory('metrics', factory, subparser)
    return parser


def main(parser, args):
    if args.reference_type == 'argument':
        ref = core.PlainText(args.reference)
    else:
        ref = core.File(args.reference, args.reference_type)

    if args.hypothesis_type == 'argument':
        hyp = core.PlainText(args.hypothesis)
    else:
        hyp = core.File(args.hypothesis, args.hypothesis_type)

    ref = list(ref)
    hyp = list(hyp)

    if 'metrics' not in args or not len(args.metrics):
        parser.error("need at least one metric")

    for item in args.metrics:
        metric_name = item.pop(0).replace('-', '.')
        print(metric_name)
        print('=' * len(metric_name))
        print()
        metric = factory.create(metric_name, *item)
        # todo: different output options
        print(metric.compare(ref, hyp))
        print()
