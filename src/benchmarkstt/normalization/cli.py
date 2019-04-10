"""
Apply normalization to given input
"""

import sys
from . import NormalizationComposite
import argparse
from . import factory
import textwrap
import itertools
from .logger import DiffLoggingFormatter, normalize_logger
import logging
from benchmarkstt.cli import args_inputfile


class _NormalizerAction:
    """
    Placeholder class to recognize an argument is a NormalizerAction in argparse
    """


def normalizer_action(required_args, optional_args):
    """
    Custom argparse action to support a variable amount of arguments
    :param list required_args: required arguments
    :param list optional_args: optional arguments
    :rtype: NormalizerAction
    """

    minlen = len(required_args)
    maxlen = minlen + len(optional_args)

    class NormalizerAction(argparse.Action, _NormalizerAction):
        def __call__(self, parser, args, values, option_string=None):
            if len(values) < minlen or len(values) > maxlen:
                raise argparse.ArgumentTypeError('argument "%s" requires between %d and %d arguments (got %d)' %
                                                 (self.dest, minlen, maxlen, len(values)))

            if 'normalizers' not in args:
                args.normalizers = []

            args.normalizers.append([self.dest] + values)

    return NormalizerAction


class Formatter(argparse.HelpFormatter):
    """
    Custom formatter for argparse that allows us to properly display _NormalizerActions and docblock documentation
    """

    def _format_args(self, action, default_metavar):
        if isinstance(action, _NormalizerAction):
            return ' '.join(action.metavar)

        return super()._format_args(action, default_metavar)

    def _split_lines(self, text, width):
        def wrap(txt):
            if txt == '':
                return ['']
            return textwrap.wrap(txt, width=width)

        text = text.splitlines()
        text = list(itertools.chain.from_iterable(map(wrap, text)))
        return text


def argparser(parser: argparse.ArgumentParser):
    """
    Adds the help and arguments specific to this module
    """

    parser.add_argument('--log', action='store_true',
                        help='show normalizer logs')

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

    normalizers_desc = """
      A list of normalizers to execute on the input, can be one or more normalizers
      which are applied sequentially.
      The program will automatically find the normalizer in benchmarkstt.normalization.core,
      then benchmarkstt.normalization and finally in the global namespace.
      At least one normalizer needs to be provided."""

    normalizers = parser.add_argument_group('available normalizers', description=normalizers_desc)

    for conf in factory:
        name = conf.name
        docs = conf.docs

        arguments = dict()
        arguments['help'] = docs
        arguments['nargs'] = 0

        if len(conf.required_args) or len(conf.optional_args):
            arguments['nargs'] = '+'
            optionals = list(map(lambda x: '[%s]' % x, conf.optional_args))
            arguments['metavar'] = tuple(conf.required_args + optionals)

        arguments['action'] = normalizer_action(conf.required_args, conf.optional_args)

        normalizers.add_argument('--%s' % (name,), **arguments)

    return parser


def main(parser, args):
    input_files = [f[0] for f in args.inputfile] if args.inputfile else None
    output_files = [f[0] for f in args.outputfile] if args.outputfile else None

    if 'normalizers' not in args or not len(args.normalizers):
        parser.error("need at least one normalizer")

    if input_files is None and output_files is not None and len(output_files) > 1:
        parser.error("can only write output to one file when reading from stdin")
    elif input_files is not None and output_files is not None:
        # straight mapping from input to output, needs equal length
        if len(input_files) != len(output_files):
            parser.error("when using multiple input or output files, there needs to be an equal amount of each")

    if args.log:
        handler = logging.StreamHandler()
        handler.setFormatter(DiffLoggingFormatter('cli'))
        handler.setLevel(logging.INFO)
        normalize_logger.addHandler(handler)

    composite = NormalizationComposite()
    for item in args.normalizers:
        normalizer_name = item.pop(0).replace('-', '.')
        normalizer = factory.create(normalizer_name, *item)
        composite.add(normalizer)

    if output_files is not None:
        # pre-open the output files before doing the grunt work
        output_files = [open(output_file, 'xt') for output_file in output_files]

    if input_files is not None:
        for idx, file in enumerate(input_files):
            with open(file) as input_file:
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
        if output_files is None:
            sys.stdout.write(text)
        else:
            output_file = output_files[0]
            output_file.write(text)
            output_file.close()
