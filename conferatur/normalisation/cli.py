"""
.. code-block:: none

    usage: normalisation [--help|-h]
                         [--input-file|-i FILE]
                         [--output-file|-o FILE]
                         [--list-normalisers]
                         --normaliser-name [argument ...]
                         [--normaliser-name [argument ...] ...]

    positional arguments:
      -h, --help              show this help message and exit

    optional arguments:
      You can provide multiple input and output files, each preceded by -i and -o
      respectively.
      If no input file is given, only one output file can be used.
      If using both multiple input and output files there should be an equal amount
      of each. Each processed input file will then be written to the corresponding
      output file.


      --list-normalisers      list available default normalisers

      !!! WARNING: OUTPUT FILES ARE OVERWRITTEN IF THEY ALREADY EXIST !!!

    normalisers:
      A list of normalisers to execute on the input, can be one or more normalisers
      which are applied sequentially.
      The program will automatically find the normaliser in conferatur.normalisation.core,
      then conferatur.normalisation and finally in the global namespace.
      At least one normaliser needs to be provided.

      --normaliser-name [arguments ...]
                               the name of the normaliser (eg. --lowercase),
                               optionally followed by arguments passed to the
                               normaliser
"""

import sys
from . import core
import inspect
import re
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


class NormaliserFormatter(argparse.HelpFormatter):
    def _format_args(self, action, default_metavar):
        if isinstance(action, _NormaliserAction):
            return ' '.join(action.metavar)

        return super()._format_args(action, default_metavar)


def get_parser(parser=None):
    if parser is None:
        parser = argparse.ArgumentParser(prog='normalisation',
                                         formatter_class=NormaliserFormatter)

    parser.add_argument('-i', '--inputfile', action='append', nargs="?",
                        help='read input from this file, defaults to STDIN')
    parser.add_argument('-o', '--outputfile', action='append', nargs="?",
                        help='write output to this file, defaults to STDOUT')

    normalisers = parser.add_argument_group('Available normalisers')

    for name, cls, docs, args, optional_args in get_normalisers():
        arguments = dict()
        arguments['help'] = docs

        if not len(args) and not len(optional_args):
            arguments['action'] = 'store_true'
            arguments['nargs'] = 0
            arguments['action'] = normaliser_action(args, optional_args)
        else:
            arguments['nargs'] = '+'
            optionals = list(map(lambda x: '[%s]' % x, optional_args))
            arguments['metavar'] = tuple(args + optionals)
            arguments['action'] = normaliser_action(args, optional_args)

        # print(arguments)
        normalisers.add_argument('--%s' % (name,), **arguments)

    return parser


def get_normalisers():
    ignored_normalisers = ('commandlinearguments', 'composite')
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

        have_defaults = len(args) - len(defaults)

        required_args = args[0:have_defaults]

        optional_args = args[have_defaults:]

        yield name, cls, docs, required_args, optional_args


def main(parser, args=None):
    input_files = args.inputfile
    output_files = args.outputfile
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

    if input_files is not None:
        for idx, file in enumerate(input_files):
            with open(file) as input_file:
                text = input_file.read()
            text = composite.normalise(text)
            if output_files is None:
                sys.stdout.write(text)
            else:
                with open(output_files[idx], 'w') as output_file:
                    output_file.write(text)
    else:
        text = sys.stdin.read()
        text = composite.normalise(text)
        if output_files is None:
            sys.stdout.write(text)
        else:
            with open(output_files[0], 'w') as output_file:
                output_file.write(text)


if __name__ == '__main__':
    main(sys.argv[1:])
