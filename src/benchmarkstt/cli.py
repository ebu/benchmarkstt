import argparse
import logging
from . import __meta__
import textwrap
import itertools
from benchmarkstt.modules import Modules


def _parser_no_sub(dont_add_submodule=False):
    parser = argparse.ArgumentParser(prog='benchmarkstt', add_help=__name__ != '__main__',
                                     description='BenchmarkSTT main command line script')

    parser.add_argument('--log-level', type=str.lower, default='warning', dest='log_level',
                        choices=list(map(str.lower, logging._nameToLevel.keys())),
                        help='set the logging output level')

    parser.add_argument('--version', action='store_true',
                        help='output benchmarkstt version number')

    # this is for argparse autodoc purposes
    if not dont_add_submodule:  # pragma: no cover
        parser.add_argument('subcommand', choices=Modules('cli').keys())

    return parser


def _parser() -> argparse.ArgumentParser:
    parser = _parser_no_sub(True)
    subparsers = parser.add_subparsers(dest='subcommand')

    for module, cli in Modules('cli'):
        kwargs = dict()
        if hasattr(cli, 'Formatter'):
            kwargs['formatter_class'] = cli.Formatter
        else:
            kwargs['formatter_class'] = ActionWithArgumentsFormatter

        if cli.__doc__ is None:
            docs = 'TODO: add description to benchmarkstt.%s.cli' % (module,)
        else:
            docs = cli.__doc__
        kwargs['description'] = textwrap.dedent(docs)
        subparser = subparsers.add_parser(module, add_help=False, **kwargs)

        subparser.add_argument('--help', action='help', default=argparse.SUPPRESS,
                               help=argparse._('show this help message and exit'))
        cli.argparser(subparser)

    return parser


def args_inputfile(parser):
    parser.add_argument('-i', '--inputfile', action='append', nargs=1,
                        help='read input from this file, defaults to STDIN',
                        metavar='file')


def args_from_factory(action, factory, parser):
    for conf in factory:
        name = conf.name
        docs = conf.docs

        arguments = dict()
        arguments['help'] = docs
        arguments['nargs'] = 0

        if len(conf.required_args) or len(conf.optional_args):
            arguments['nargs'] = '+' if len(conf.required_args) else '*'
            optionals = list(map(lambda x: '[%s]' % x, conf.optional_args))
            arguments['metavar'] = tuple(conf.required_args + optionals)

        arguments['action'] = action_with_arguments(action,
                                                    conf.required_args,
                                                    conf.optional_args)

        parser.add_argument('--%s' % (name,), **arguments)


class _ActionWithArguments:
    """
    Placeholder class to recognize an argument is a NormalizerAction in argparse
    """


def action_with_arguments(action, required_args, optional_args):
    """
    Custom argparse action to support a variable amount of arguments
    :param str action: name of the action
    :param list required_args: required arguments
    :param list optional_args: optional arguments
    :rtype: ActionWithArguments
    """

    minlen = len(required_args)
    maxlen = minlen + len(optional_args)

    class ActionWithArguments(argparse.Action, _ActionWithArguments):
        def __call__(self, parser, args, values, option_string=None):
            if len(values) < minlen or len(values) > maxlen:
                raise argparse.ArgumentTypeError('argument "%s" requires between %d and %d arguments (got %d)' %
                                                 (self.dest, minlen, maxlen, len(values)))

            if not hasattr(args, action):
                setattr(args, action, [])

            getattr(args, action).append([self.dest] + values)

    return ActionWithArguments


class ActionWithArgumentsFormatter(argparse.HelpFormatter):
    """
    Custom formatter for argparse that allows us to properly display _ActionWithArguments and docblock documentation
    """

    def _format_args(self, action, default_metavar):
        if isinstance(action, _ActionWithArguments):
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


def main():
    parser = _parser()

    try:
        # support argument completion if package is installed
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:  # pragma: no cover
        pass

    args = parser.parse_args()
    if args.version:
        print("benchmarkstt: %s" % (__meta__.__version__,))
        parser.exit(0)

    logging.basicConfig(level=args.log_level.upper())
    logging.getLogger().setLevel(args.log_level.upper())

    if not args.subcommand:
        parser.error("expects at least 1 argument")
    Modules('cli')[args.subcommand].main(parser, args)
    exit(0)


if __name__ == '__main__':  # pragma: nocover
    main()
