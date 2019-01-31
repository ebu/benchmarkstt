import argparse
import logging
from importlib import import_module
import sys
from .normalisation import cli as normalisation_cli


def _parser():
    parser = argparse.ArgumentParser(prog='conferatur', add_help=__name__ != '__main__',
                                     description='Conferatur main command line script')

    parser.add_argument('--log-level', type=str.lower, default='warning', dest='log_level',
                        choices=list(map(str.lower, logging._nameToLevel.keys())),
                        help='set the logging output level')

    subparsers = parser.add_subparsers(dest='module')
    normalisation_parser = subparsers.add_parser('normalisation',
                                                 help='Do normalisation',
                                                 formatter_class=normalisation_cli.NormaliserFormatter)
    normalisation_parser = normalisation_cli.get_parser(normalisation_parser)

    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        parser.print_help()
        parser.exit(1)

    return parser


def main():
    parser = _parser()
    args, unknown = parser.parse_known_args()

    logging.basicConfig(level=args.log_level.upper())
    module = args.module
    module = import_module('conferatur.%s.cli' % (module,))
    module.main(parser, args)


if __name__ == '__main__':
    main()
