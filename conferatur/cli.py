import argparse
import logging
from . import get_modules_dict
import textwrap
from . import __meta__

modules = get_modules_dict('cli')


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='conferatur', add_help=__name__ != '__main__',
                                     description='Conferatur main command line script')

    parser.add_argument('--log-level', type=str.lower, default='warning', dest='log_level',
                        choices=list(map(str.lower, logging._nameToLevel.keys())),
                        help='set the logging output level')

    parser.add_argument('--version', action='store_true',
                        help='output conferatur version number')

    subparsers = parser.add_subparsers(dest='subcommand')

    for module, cli in modules.items():
        if not hasattr(cli, 'argparser'):
            subparsers.add_parser(module)
            continue
        kwargs = dict()
        if hasattr(cli, 'Formatter'):
            kwargs['formatter_class'] = cli.Formatter
        kwargs['description'] = textwrap.dedent(cli.__doc__)
        subparser = subparsers.add_parser(module, **kwargs)
        cli.argparser(subparser)

    return parser


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
        print("conferatur: %s" % (__meta__.__version__,))
        parser.exit(0)

    logging.basicConfig(level=args.log_level.upper())

    if not args.subcommand:
        parser.error("expects at least 1 argument")
    modules[args.subcommand].main(parser, args)


if __name__ == '__main__':
    main()
