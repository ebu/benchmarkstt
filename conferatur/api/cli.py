"""
Make conferatur available through a rudimentary jsonapi interface
"""

from jsonrpcserver import method, serve
from conferatur import __meta__

from conferatur.normalisation import core


def argparser(parser):
    parser.add_argument('--host', help='hostname or ip to serve api')
    parser.add_argument('--port', type=int, help='port used by the server', default=5000)
    return parser


@method
def version():
    return __meta__.__version__


@method
def normalisation(text, normalisers):
    assert type(text) is str
    assert type(normalisers) is list
    assert len(normalisers)

    composite = core.Composite()
    for args in normalisers:
        assert len(args)
        normaliser = core.name_to_normaliser(args.pop(0))
        composite.add(normaliser(*args))
    return composite.normalise(text)


def main(parser, args):
    serve(args.host if args.host else '', port=args.port)

