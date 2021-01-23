import textwrap
import logging
from benchmarkstt.cli import create_parser, args_help, args_common, args_complete
from benchmarkstt.cli import CustomHelpFormatter, before_parseargs
from benchmarkstt.modules import Modules


logger = logging.getLogger(__name__)


def argparser():
    name = 'benchmarkstt-tools'
    desc = 'Some additional helpful tools'
    parser = create_parser(prog=name, description=desc)

    subparsers = parser.add_subparsers(dest='subcommand')

    for module, cli in Modules('cli'):
        kwargs = dict()
        if hasattr(cli, 'Formatter'):
            kwargs['formatter_class'] = cli.Formatter
        else:
            kwargs['formatter_class'] = CustomHelpFormatter

        if cli.__doc__ is not None:
            docs = cli.__doc__
        else:
            docs = '?'
            logger.warning('Missing __doc__ for benchmarkstt.%s._cli', module)

        kwargs['description'] = textwrap.dedent(docs)
        subparser = subparsers.add_parser(module, add_help=False, allow_abbrev=False, **kwargs)

        cli.argparser(subparser)
        args_common(subparser)
        args_help(subparser)

    args_help(parser)
    return parser


def run():
    before_parseargs()

    parser = argparser()
    args_complete(parser)

    args = parser.parse_args()

    if not args.subcommand:
        parser.error("expects at least 1 argument")

    Modules('cli')[args.subcommand].run(parser, args)
    exit(0)


if __name__ == '__main__':  # pragma: nocover
    run()
