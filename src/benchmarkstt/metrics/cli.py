from benchmarkstt.metrics.core import WER, WordDiffs, DiffCounts
from benchmarkstt.input import core
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

    parser.add_argument('-m', '--metric', default='wer',
                        help='The type of metric to run')

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

    # TODO: load proper metric class
    # TODO: provide output types

    metrics = [WordDiffs, WER, DiffCounts]
    for metric in metrics:
        cls = metric()
        print(type(cls).__name__ + ':')
        print('=' * (len(type(cls).__name__)+1))
        print()
        print(cls.compare(ref, hyp))
        print()
        print()

