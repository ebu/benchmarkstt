import argparse
import logging
import textwrap
import itertools
from benchmarkstt.modules import Modules
from benchmarkstt import __meta__
from benchmarkstt.normalization.core import Config
from argparse import ArgumentError
from contextlib import contextmanager
import sys
from functools import partial
import re

# allow loading of modules based on current working directory
sys.path.insert(0, '')


def args_help(parser):
    parser.add_argument('--help', action='help', default=argparse.SUPPRESS,
                        help=argparse._('Show this help message and exit'))


def args_common(parser):
    parser.add_argument('--log-level', type=str.lower, default='warning', dest='log_level',
                        choices=list(map(str.lower, logging._nameToLevel.keys())),
                        help=argparse._('Set the logging output level'))


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
                if minlen == maxlen:
                    lentxt = str(minlen)
                else:
                    lentxt = 'between %d and % d' % (minlen, maxlen)
                raise ArgumentError(self, 'requires %s arguments (got %d)' % (lentxt, len(values)))

            if not hasattr(args, action):
                setattr(args, action, [])

            getattr(args, action).append([self.dest] + values)

    return ActionWithArguments


# TODO: further augment formatter to give cleaner output
class HelpFormatter(argparse.HelpFormatter):
    """
    Custom formatter for argparse that allows us to properly display _ActionWithArguments and docblock documentation,
    as well as allowing newlines inside the description.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._whitespace_matcher = re.compile(r'[\t ]+', re.ASCII)

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

    def _fill_text(self, text, width, indent):
        text = self._whitespace_matcher.sub(' ', text).strip()
        wrapper = partial(textwrap.fill,
                          width=width,
                          initial_indent=indent,
                          subsequent_indent=indent)
        return '\n'.join(map(wrapper, text.split('\n')))


def args_complete(parser):  # pragma: no cover
    try:
        # support argument completion if package is installed
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:
        pass


def create_parser(*args, **kwargs):
    defaults = {
        'add_help': False,
        'formatter_class': HelpFormatter,
        'allow_abbrev': False,
    }
    kwargs = {k: kwargs.get(k, v) for k, v in defaults.items()}
    parser = argparse.ArgumentParser(*args, **kwargs)
    parser._optionals.title = 'named arguments'
    return parser


@contextmanager
def main_parser_context():
    try:
        # import done here to avoid circular references
        import benchmarkstt.benchmark.cli as benchmark_cli
        name = 'benchmarkstt'
        desc = 'BenchmarkSTT\'s main command line tool that is used for benchmarking speech-to-text, ' \
               'for additional tools, see ``benchmarkstt-tools --help``.'

        parser = create_parser(prog=name, description=desc)
        benchmark_cli.argparser(parser)

        parser.add_argument('--version', action='store_true',
                            help='Output %s version number' % (name,))

        args_common(parser)
        args_help(parser)
        yield parser
    finally:
        pass


def determine_log_level():
    # Set log-level manually before parse_args(), so that also factory logs, etc. get output
    log_level = 'WARNING'
    if '--log-level' in sys.argv:
        idx = sys.argv.index('--log-level') + 1
        if idx < len(sys.argv):
            if sys.argv[idx].upper() in logging._nameToLevel:
                log_level = sys.argv[idx].upper()

    logging.basicConfig(level=log_level)
    logging.getLogger().setLevel(log_level)


def main():
    determine_log_level()
    # import done here to avoid circular dependencies
    import benchmarkstt.benchmark.cli as benchmark_cli
    with main_parser_context() as parser:
        args_complete(parser)

        if '--version' in sys.argv:
            print("benchmarkstt: %s" % (__meta__.__version__,))
            logging.getLogger().info('python version: %s', sys.version)
            parser.exit(0)

        args = parser.parse_args()
        benchmark_cli.main(parser, args)

    exit(0)


def main_parser():
    with main_parser_context() as parser:
        return parser


def tools_parser():
    name = 'benchmarkstt-tools'
    desc = 'Some additional helpful tools'
    parser = create_parser(prog=name, description=desc)

    subparsers = parser.add_subparsers(dest='subcommand')

    for module, cli in Modules('cli'):
        kwargs = dict()
        if hasattr(cli, 'Formatter'):
            kwargs['formatter_class'] = cli.Formatter
        else:
            kwargs['formatter_class'] = HelpFormatter

        docs = cli.__doc__ if cli.__doc__ is not None else ('TODO: add description to benchmarkstt.%s.cli' % (module,))
        kwargs['description'] = textwrap.dedent(docs)
        subparser = subparsers.add_parser(module, add_help=False, allow_abbrev=False, **kwargs)

        cli.argparser(subparser)
        args_common(subparser)
        args_help(subparser)

    args_help(parser)
    return parser


def tools():
    determine_log_level()
    parser = tools_parser()
    args_complete(parser)

    args = parser.parse_args()

    if not args.subcommand:
        parser.error("expects at least 1 argument")

    Modules('cli')[args.subcommand].main(parser, args)
    exit(0)


if __name__ == '__main__':  # pragma: nocover
    main()
