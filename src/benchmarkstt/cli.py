import argparse
import logging
import textwrap
import itertools
from benchmarkstt.modules import Modules
from benchmarkstt import __meta__
from benchmarkstt.normalization.core import Config
import sys


def args_help(parser):
    parser.add_argument('--help', action='help', default=argparse.SUPPRESS,
                        help=argparse._('show this help message and exit'))


def args_common(parser):
    parser.add_argument('--log-level', type=str.lower, default='warning', dest='log_level',
                        choices=list(map(str.lower, logging._nameToLevel.keys())),
                        help=argparse._('set the logging output level'))


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


def args_complete(parser):
    try:
        # support argument completion if package is installed
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:  # pragma: no cover
        pass


def main_parser():
    name = 'benchmarkstt'
    desc = 'BenchmarkSTT main command line script, for additional tools, see ``benchmarkstt-tools --help``.'
    parser = argparse.ArgumentParser(prog=name, add_help=False,
                                     description=desc,
                                     formatter_class=ActionWithArgumentsFormatter)

    Modules('cli')['benchmark'].argparser(parser)

    parser.add_argument('--version', action='store_true',
                        help='output %s version number' % (name,))

    args_common(parser)
    args_help(parser)
    return parser


def main():
    parser = main_parser()
    args_complete(parser)

    if '--version' in sys.argv:
        print("benchmarkstt: %s" % (__meta__.__version__,))
        parser.exit(0)

    args = parser.parse_args()

    log_level = args.log_level.upper() if 'log_level' in args else 'WARNING'
    logging.basicConfig(level=log_level)
    logging.getLogger().setLevel(log_level)

    Config.default_section = 'normalization'
    Modules('cli')['benchmark'].main(parser, args)
    exit(0)


def tools_parser():
    name = 'benchmarkstt-tools'
    parser = argparse.ArgumentParser(prog=name, add_help=False,
                                     description='BenchmarkSTT command line script for tools')

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

        cli.argparser(subparser)
        args_common(subparser)
        args_help(subparser)

    args_help(parser)
    return parser


def tools():
    parser = tools_parser()
    args_complete(parser)

    args = parser.parse_args()

    log_level = args.log_level.upper() if 'log_level' in args else 'WARNING'
    logging.basicConfig(level=log_level)
    logging.getLogger().setLevel(log_level)

    if not args.subcommand:
        parser.error("expects at least 1 argument")

    Modules('cli')[args.subcommand].main(parser, args)
    exit(0)


if __name__ == '__main__':  # pragma: nocover
    main()
