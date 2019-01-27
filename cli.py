import argparse
import logging
from importlib import import_module
import sys


def main():
    modules = ['normalisation', 'someother']

    parser = argparse.ArgumentParser(prog='conferatur', add_help=False,
                                     description='Conferatur main command line script')
    parser.add_argument('module', choices=modules, help="the module to run")
    parser.add_argument('--log-level', type=str.lower, default='warning', dest='log_level',
                        choices=list(map(str.lower, logging._nameToLevel.keys())),
                        help='set the logging output level (default: warning)')

    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        parser.print_help()
        parser.exit(1)

    args, unknown = parser.parse_known_args()

    logging.basicConfig(level=args.log_level.upper())
    module = import_module('conferatur.%s.cli' % (args.module,))
    module.main(unknown)


if __name__ == '__main__':
    main()
