import logging
import sys
from contextlib import contextmanager
from benchmarkstt import __meta__
from benchmarkstt.cli import create_parser, args_help, args_common, determine_log_level, args_complete


@contextmanager
def parser_context():
    try:
        # import done here to avoid circular references
        import benchmarkstt.cli.entrypoints.benchmark as benchmark_cli
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


def main_parser():
    with parser_context() as parser:
        return parser


def run():
    determine_log_level()
    # import done here to avoid circular dependencies
    import benchmarkstt.cli.entrypoints.benchmark as entrypoint
    with parser_context() as parser:
        args_complete(parser)

        if '--version' in sys.argv:
            print("benchmarkstt: %s" % (__meta__.__version__,))
            logging.getLogger().info('python version: %s', sys.version)
            parser.exit(0)

        args = parser.parse_args()
        entrypoint.run(parser, args)

    exit(0)


if __name__ == '__main__':  # pragma: nocover
    run()
