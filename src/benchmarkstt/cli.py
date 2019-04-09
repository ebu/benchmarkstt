import argparse
import logging
import textwrap
from importlib import import_module
from . import __meta__


def get_modules(sub_module=None):
    postfix = '' if sub_module is None else '.' + sub_module
    for module in modules:
        yield module, import_module('benchmarkstt.%s%s' % (module, postfix))


def get_modules_dict(sub_module=None):
    return {module: cli for module, cli in get_modules(sub_module)}


def modules():
    return get_modules_dict('cli')


def _parser_no_sub(dont_add_submodule=False):
    parser = argparse.ArgumentParser(prog='benchmarkstt', add_help=__name__ != '__main__',
                                     description='BenchmarkSTT main command line script')

    parser.add_argument('--log-level', type=str.lower, default='warning', dest='log_level',
                        choices=list(map(str.lower, logging._nameToLevel.keys())),
                        help='set the logging output level')

    parser.add_argument('--version', action='store_true',
                        help='output benchmarkstt version number')

    # this is for argpars autodoc purposes
    if not dont_add_submodule:
        parser.add_argument('subcommand', choices=modules().keys())

    return parser


def _parser() -> argparse.ArgumentParser:
    parser = _parser_no_sub(True)
    subparsers = parser.add_subparsers(dest='subcommand')

    for module, cli in modules().items():
        if not hasattr(cli, 'argparser'):
            subparsers.add_parser(module)
            continue
        kwargs = dict()
        if hasattr(cli, 'Formatter'):
            kwargs['formatter_class'] = cli.Formatter

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


def main():
    parser = _parser()

    try:
        # support argument completion if package is installed
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:
        pass
    args = parser.parse_args()
    if args.version:
        print("benchmarkstt: %s" % (__meta__.__version__,))
        parser.exit(0)

    logging.basicConfig(level=args.log_level.upper())
    logging.getLogger().setLevel(args.log_level.upper())

    if not args.subcommand:
        parser.error("expects at least 1 argument")
    modules()[args.subcommand].main(parser, args)


if __name__ == '__main__':
    main()
