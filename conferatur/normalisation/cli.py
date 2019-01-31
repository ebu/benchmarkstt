"""
Apply normalisation to given input
"""

import sys
from . import core
import inspect
import textwrap
import argparse


class _NormaliserAction:
    # placeholder to recognize it is a NormaliserAction
    pass


def normaliser_action(required_args, optional_args):
    minlen = len(required_args)
    maxlen = minlen + len(optional_args)

    class NormaliserAction(argparse.Action, _NormaliserAction):
        def __call__(self, parser, args, values, option_string=None):
            if len(values) < minlen or len(values) > maxlen:
                raise argparse.ArgumentTypeError('argument "%s" requires between %d and %d arguments (got %d)' %
                                                 (self.dest, minlen, maxlen, len(values)))

            if 'normalisers' not in args:
                args.normalisers = []

            args.normalisers.append([self.dest] + values)

    return NormaliserAction


class Formatter(argparse.HelpFormatter):
    def _format_args(self, action, default_metavar):
        if isinstance(action, _NormaliserAction):
            return ' '.join(action.metavar)

        return super()._format_args(action, default_metavar)


def argparser(parser=None):
    if parser is None:
        parser = argparse.ArgumentParser(prog='normalisation',
                                         formatter_class=Formatter,
                                         description='Apply one or more normalisers to the input')

    files_desc = """
      You can provide multiple input and output files, each preceded by -i and -o
      respectively.
      If no input file is given, only one output file can be used.
      If using both multiple input and output files there should be an equal amount
      of each. Each processed input file will then be written to the corresponding
      output file."""

    files = parser.add_argument_group('input and output files', description=files_desc)

    files.add_argument('-i', '--inputfile', action='append', nargs=1,
                       help='read input from this file, defaults to STDIN',
                       metavar='file')
    files.add_argument('-o', '--outputfile', action='append', nargs=1,
                       help='write output to this file, defaults to STDOUT',
                       metavar='file')

    normalisers_desc = """
      A list of normalisers to execute on the input, can be one or more normalisers
      which are applied sequentially.
      The program will automatically find the normaliser in conferatur.normalisation.core,
      then conferatur.normalisation and finally in the global namespace.
      At least one normaliser needs to be provided."""

    normalisers = parser.add_argument_group('Available normalisers', description=normalisers_desc)

    for name, cls, docs, args, optional_args in get_normalisers():
        arguments = dict()
        arguments['help'] = docs
        arguments['nargs'] = 0

        if len(args) or len(optional_args):
            arguments['nargs'] = '+'
            optionals = list(map(lambda x: '[%s]' % x, optional_args))
            arguments['metavar'] = tuple(args + optionals)

        arguments['action'] = normaliser_action(args, optional_args)

        normalisers.add_argument('--%s' % (name,), **arguments)

    return parser


def get_normalisers():
    ignored_normalisers = ('composite',)
    for cls in dir(core):
        name = cls.lower()
        cls = getattr(core, cls)
        if name in ignored_normalisers:
            continue
        if not inspect.isclass(cls):
            continue
        if not hasattr(cls, 'normalise'):
            continue

        docs = cls.__doc__.split('.. ', 1)[0]
        docs = docs.split(':param', 1)[0]
        docs = textwrap.dedent(docs)

        argspec = inspect.getfullargspec(cls.__init__)
        args = list(argspec.args)[1:]
        defaults = []
        if argspec.defaults:
            defaults = list(argspec.defaults)

        defaults_idx = len(args) - len(defaults)
        required_args = args[0:defaults_idx]
        optional_args = args[defaults_idx:]

        yield name, cls, docs, required_args, optional_args


def main(parser, args=None):
    input_files = [f[0] for f in args.inputfile] if args.inputfile else None
    output_files = [f[0] for f in args.outputfile] if args.outputfile else None

    if 'normalisers' not in args or not len(args.normalisers):
        parser.error("need at least one normaliser")

    if input_files is None and output_files is not None and len(output_files) > 1:
        parser.error("can only write output to one file when reading from stdin")
    elif input_files is not None and output_files is not None:
        # straight mapping from input to output, needs equal length
        if len(input_files) != len(output_files):
            parser.error("when using multiple input or output files, there needs to be an equal amount of each")

    composite = core.Composite()
    for item in args.normalisers:
        normaliser_name = item.pop(0).replace('-', '.')
        cls = core.name_to_normaliser(normaliser_name)
        composite.add(cls(*item))

    if output_files is not None:
        # pre-open the output files before doing the grunt work
        output_files = [open(output_file, 'xt') for output_file in output_files]

    if input_files is not None:
        for idx, file in enumerate(input_files):
            with open(file) as input_file:
                text = input_file.read()
            text = composite.normalise(text)
            if output_files is None:
                sys.stdout.write(text)
            else:
                output_file = output_files[idx]
                output_file.write(text)
                output_file.close()
    else:
        text = sys.stdin.read()
        text = composite.normalise(text)
        if output_files is None:
            sys.stdout.write(text)
        else:
            output_file = output_files[0]
            output_file.write(text)
            output_file.close()


if __name__ == '__main__':
    _parser = argparser()
    main(_parser, _parser.parse_args())
