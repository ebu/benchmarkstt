"""
Make conferatur available through a rudimentary JSON-RPC_ interface

.. _JSON-RPC: https://www.jsonrpc.org

"""

import jsonrpcserver
import json
from conferatur import __meta__
from conferatur.normalization import core, name_to_normalizer, available_normalizers
from functools import wraps
from conferatur.docblock import format_docs
import inspect
import os
import conferatur.csv as csv


def get_methods() -> jsonrpcserver.methods.Methods:
    """
    Returns the available JSON-RPC api methods

    :return: jsonrpcserver.methods.Methods
    """

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

    normalizers = available_normalizers()

    @method
    def normalization_list():
        """
        Get a list of available core normalizers

        :return object: With key being the normalizer name, and value its description
        """
        return {name: conf.docs
                for name, conf in normalizers.items()}

    def is_safe_path(path):
        """
        Determines whether the file or path is within the current working directory
        :param str|PathLike path:
        :return: bool
        """
        return os.path.abspath(path).startswith(os.path.abspath(os.getcwd()))

    class SecurityError(ValueError):
        """Trying to do or access something that isn't allowed"""

    def serve_normalizer(config):
        cls = config.cls

        @wraps(cls)
        def _(text, *args, **kwargs):
            # only allow files from cwd to be used...
            try:
                if 'file' in kwargs:
                    if not is_safe_path(kwargs['file']):
                        raise SecurityError("Access to unallowed file attempted", 'file')

                if 'path' in kwargs:
                    if not is_safe_path(kwargs['path']):
                        raise SecurityError("Access to unallowed directory attempted", 'path')

                return cls(*args, **kwargs).normalize(text)
            except csv.CSVParserError as e:
                message = 'on line %d, character %d' % (e.line, e.char)
                message = '\n'.join([e.__doc__, e.message, message])
                data = {
                    "message": message,
                    "line": e.line,
                    "char": e.char,
                    "index": e.index,
                    "field": "config"
                }
                raise AssertionError(json.dumps(data))
            except SecurityError as e:
                data = {
                    "message": e.args[0],
                    "field": e.args[1]
                }
                raise AssertionError(json.dumps(data))

        # copy signature from original normalizer, and add text param
        sig = inspect.signature(cls)
        params = [inspect.Parameter('text', kind=inspect.Parameter.POSITIONAL_OR_KEYWORD)]
        params.extend(sig.parameters.values())
        sig = sig.replace(parameters=params)
        _.__signature__ = sig
        _.__doc__ += '\n    :param str text: The text to normalize'

        # todo (?) add available files and folders as select options
        return _

    # add each normalizer as its own api call
    for conf in normalizers.values():
        method(serve_normalizer(conf), name='normalization.%s' % (conf.name,))

    @method
    def _help():
        """
        Returns available api methods

        :return object: With key being the method name, and value its description
        """

        return {name: format_docs(func.__doc__)
                for name, func in methods.items.items()}

    return methods

