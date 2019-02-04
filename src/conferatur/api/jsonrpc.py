"""
Make conferatur available through a rudimentary JSON-RPC_ interface

.. _JSON-RPC: https://www.jsonrpc.org

"""

import jsonrpcserver
from conferatur import __meta__
from conferatur.normalisation import core, name_to_normaliser, available_normalisers
from functools import wraps
from conferatur import format_docs


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

