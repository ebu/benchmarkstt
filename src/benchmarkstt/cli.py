import argparse
import logging
from . import get_modules_dict
import textwrap
from . import __meta__


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
        docs = cli.__doc__
        kwargs['description'] = textwrap.dedent(docs if docs is not None else '')
        subparser = subparsers.add_parser(module, **kwargs)
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
