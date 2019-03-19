import argparse
from benchmarkstt.metrics.core import WER
from benchmarkstt.input import core


def argparser(parser: argparse.ArgumentParser):
    # steps: input tokenization normalize compare
    parser.add_argument('--input-ref', nargs='+', required=True)
    parser.add_argument('--input-hyp', nargs='+', required=True)

    return parser


def create_input(*args):
    # todo: support multiple input formats
    if len(args) == 1:
        return core.File(args[0])

    raise ValueError("Currently only File is supported")


def main(parser, args):

    ref = create_input(*args.input_ref)
    hyp = create_input(*args.input_hyp)

    comparison = WER()
    print(comparison.compare(ref.schema(), hyp.schema()))
    print(ref)
    print(hyp)
