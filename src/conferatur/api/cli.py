"""
Make conferatur available through a rudimentary JSON-RPC_ interface

.. _JSON-RPC: https://www.jsonrpc.org

"""

from jsonrpcserver import method, serve, dispatch
from conferatur import __meta__
from flask import Flask, request, Response
from conferatur.normalisation import core, name_to_normaliser, available_normalisers


def argparser(parser):
    parser.add_argument('--debug', action='store_true', help='run in debug mode')
    parser.add_argument('--host', help='hostname or ip to serve api')
    parser.add_argument('--port', type=int, help='port used by the server', default=5000)
    parser.add_argument('--entrypoint', help='the jsonrpc api address', default='/')
    return parser


def create_app(entrypoint=None, debug=None):
    app = Flask(__name__)

    if entrypoint is None:
        entrypoint = '/'

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
            normaliser = name_to_normaliser(args.pop(0))
            composite.add(normaliser(*args))
        return composite.normalise(text)

    @method
    def list_normalisers():
        normalisers = available_normalisers()
        for name, conf in normalisers.items():
            normalisers[name] = conf.docs
        return normalisers

    @app.route(entrypoint, methods=["POST"])
    def jsonrpc():
        req = request.get_data().decode()
        response = dispatch(req, debug=debug, convert_camel_case=True)
        return Response(str(response), response.http_status, mimetype="application/json")

    return app


def main(parser, args):
    app = create_app(args.entrypoint, args.debug)
    app.run(host=args.host, port=args.port)

