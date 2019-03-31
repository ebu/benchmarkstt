import argparse
from benchmarkstt.metrics.core import WER
from benchmarkstt.input import core
import argparse


def argparser(parser: argparse.ArgumentParser):
    # steps: input normalize[pre?] segmentation normalize[post?] compare
    parser.add_argument('-r', '--reference', required=True)
    parser.add_argument('-h', '--hypothesis', required=True)

    parser.add_argument('-rt', '--reference-type', default='infer')
    parser.add_argument('-ht', '--hypothesis-type', default='infer')

    parser.add_argument('-m', '--metric', nargs='?', default='wer')

    return parser


def main(parser, args):

    ref = core.File(args.reference, args.reference_type)
    hyp = core.File(args.hypothesis, args.reference_type)
    ref = list(ref)
    hyp = list(hyp)

    metrics = WER(mode=WER.MODE_STRICT)
    print('strict: %f' % metrics.compare(ref, hyp))

    metrics = WER(mode=WER.MODE_HUNT)
    print('hunt: %f' % metrics.compare(ref, hyp))

    metrics = WER(mode=WER.MODE_DIFFLIBRATIO)
    print('difflib: %f' % metrics.compare(ref, hyp))

    # print(comparison.compare(ref.schema(), hyp.schema()))
    # print(ref)
    # print(hyp)
