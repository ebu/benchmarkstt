"""
Apply normalization to given input
"""

import sys
from . import NormalizationComposite
import argparse
from . import factory
from .logger import DiffLoggingFormatter, Logger
import logging
from benchmarkstt.cli import args_from_factory
from benchmarkstt import settings


def args_inputfile(parser):
    parser.add_argument('-i', '--inputfile', action='append', nargs=1,
                        help='read input from this file, defaults to STDIN',
                        metavar='file')


def args_logs(parser: argparse.ArgumentParser):
    parser.add_argument('--log', action='store_true',
                        help='show normalization logs (warning: for large files with many normalization rules this will'
                             ' cause a significant performance penalty and a lot of output data)')


def args_normalizers(parser: argparse.ArgumentParser):
    normalizers_desc = """
      A list of normalizers to execute on the input, can be one or more normalizers
      which are applied sequentially.
      The program will automatically find the normalizer in benchmarkstt.normalization.core,
      then benchmarkstt.normalization and finally in the global namespace.
      """

    normalizers = parser.add_argument_group('available normalizers', description=normalizers_desc)
    args_from_factory('normalizers', factory, normalizers)


def argparser(parser: argparse.ArgumentParser):
    """
    Adds the help and arguments specific to this module
    """
    args_logs(parser)

    files_desc = """
      You can provide multiple input and output files, each preceded by -i and -o
      respectively.
      If no input file is given, only one output file can be used.
      If using both multiple input and output files there should be an equal amount
      of each. Each processed input file will then be written to the corresponding
      output file."""

    files = parser.add_argument_group('input and output files', description=files_desc)
    args_inputfile(files)
    files.add_argument('-o', '--outputfile', action='append', nargs=1,
                       help='write output to this file, defaults to STDOUT',
                       metavar='file')

    args_normalizers(parser)
    return parser


def get_normalizer_from_args(args):
    if args.log:
        handler = logging.StreamHandler()
        formatter = DiffLoggingFormatter('cli', show_color_key=False)
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        Logger.logger.addHandler(handler)

    composite = NormalizationComposite()

    if 'normalizers' in args:
        for item in args.normalizers:
            normalizer_name = item.pop(0).replace('-', '.')
            normalizer = factory.create(normalizer_name, *item)
            composite.add(normalizer)

    return composite


def main(parser, args):
    input_files = [f[0] for f in args.inputfile] if args.inputfile else None
    output_files = [f[0] for f in args.outputfile] if args.outputfile else None

    if 'normalizers' not in args or not len(args.normalizers):
        parser.error("need at least one normalizer")

    if input_files is None and output_files is not None:
        parser.error("can only write output to stdout when reading from stdin")

    composite = get_normalizer_from_args(args)

    encoding = settings.default_encoding
    if output_files is not None:
        # pre-open the output files before doing the grunt work
        output_files = [open(output_file, 'xt', encoding=encoding) for output_file in output_files]

    if input_files is not None:
        for idx, file in enumerate(input_files):
            with open(file, encoding=encoding) as input_file:
                text = input_file.read()
            text = composite.normalize(text)
            if output_files is None:
                sys.stdout.write(text)
            else:
                output_file = output_files[idx]
                output_file.write(text)
                output_file.close()
    else:
        text = sys.stdin.read()
        text = composite.normalize(text)
        sys.stdout.write(text)
