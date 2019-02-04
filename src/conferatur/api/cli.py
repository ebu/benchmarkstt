"""
Make conferatur available through a rudimentary JSON-RPC_ interface

.. _JSON-RPC: https://www.jsonrpc.org

"""

import jsonrpcserver
from conferatur import __meta__
from flask import Flask, request, Response
from conferatur.normalisation import core, name_to_normaliser, available_normalisers
from functools import wraps
from conferatur import format_docs


def argparser(parser):
    parser.add_argument('--debug', action='store_true', help='run in debug mode')
    parser.add_argument('--host', help='hostname or ip to serve api')
    parser.add_argument('--port', type=int, help='port used by the server', default=5000)
    parser.add_argument('--entrypoint', help='the jsonrpc api address', default='/')
    parser.add_argument('--list-methods', action='store_true', help='list the available jsonrpc methods')
    return parser


def create_app(entrypoint=None, debug=None):
    app = Flask(__name__)

    if entrypoint is None:
        entrypoint = '/'

    methods = get_methods()

    @app.route(entrypoint, methods=["POST"])
    def jsonrpc():
        req = request.get_data().decode()
        response = jsonrpcserver.dispatch(req, methods=methods, debug=debug, convert_camel_case=True)
        return Response(str(response), response.http_status, mimetype="application/json")

    return app


def get_methods():
    methods = jsonrpcserver.methods.Methods()

    def method(f, name=None):
        if name is None:
            name = f.__name__.lstrip('_').replace('_', '.')

        methods.add(**{name: f})

    @method
    def version():
        """
        Get the version of conferatur

        :return str: Conferatur version
        """

        return __meta__.__version__

    @method
    def normalisation(text, normalisers):
        """
        Apply normalisation

        :param str text: The text to normalise
        :param list normalisers: A list of lists of normalisers to be applied
        :return str: Normalised text
        """
        assert type(text) is str
        assert type(normalisers) is list
        assert len(normalisers)

        composite = core.Composite()
        for args in normalisers:
            assert len(args)
            normaliser = name_to_normaliser(args.pop(0))
            composite.add(normaliser(*args))
        return composite.normalise(text)

    normalisers = available_normalisers()

    @method
    def normalisation_list():
        """
        Get a list of available core normalisers

        :return object: With key being the normaliser name, and value its description
        """
        return {name: conf.docs
                for name, conf in normalisers.items()}

    # add each normaliser as its own api call
    for name, conf in normalisers.items():
        normaliser = conf.cls
        f = wraps(normaliser)(lambda *args, **kwargs: normaliser(*args, **kwargs).normalise())
        f.__doc__ = format_docs(f.__doc__)
        if normaliser.__init__.__doc__:
            f.__doc__ += '\n\n' + format_docs(normaliser.__init__.__doc__)
        method(f, name='normalisation.%s' % (name.lower(),))

    @method
    def _help():
        """
        Returns available api methods

        :return object: With key being the method name, and value its description
        """

        return {name: format_docs(func.__doc__)
                for name, func in methods.items.items()}

    return methods


def main(parser, args):
    if args.list_methods:
        methods = get_methods()
        for name, func in methods.items.items():
            print('%s\n%s' % (name, '-' * len(name)))
            print('')
            print(format_docs(func.__doc__))
            print('')
    else:
        app = create_app(args.entrypoint, args.debug)
        app.run(host=args.host, port=args.port, debug=args.debug)

