import argparse
import logging
from importlib import import_module
from . import modules


def _parser():
    parser = argparse.ArgumentParser(prog='conferatur', add_help=__name__ != '__main__',
                                     description='Conferatur main command line script')

    parser.add_argument('--log-level', type=str.lower, default='warning', dest='log_level',
                        choices=list(map(str.lower, logging._nameToLevel.keys())),
                        help='set the logging output level')

    subparsers = parser.add_subparsers(dest='sub-command')
    for module in modules:
        cli = import_module('conferatur.%s.cli' % (module,))
        kwargs = dict()
        if hasattr(cli, 'Formatter'):
            kwargs['formatter_class'] = cli.Formatter
        subparser = subparsers.add_parser(module, **kwargs)
        cli.get_parser(subparser)

    return parser


def main():
    parser = _parser()
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level.upper())
    module = getattr(args, 'sub-command')
    module = import_module('conferatur.%s.cli' % (module,))
    module.main(parser, args)


if __name__ == '__main__':
    main()
