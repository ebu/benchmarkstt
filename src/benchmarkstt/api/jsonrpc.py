"""
Make benchmarkstt available through a rudimentary JSON-RPC_ interface

.. warning::
    Only supported for Python versions 3.6 and above!

.. _JSON-RPC: https://www.jsonrpc.org

"""

import jsonrpcserver
import json
from benchmarkstt import __meta__
from functools import wraps
from benchmarkstt.docblock import format_docs
from benchmarkstt.modules import Modules
from inspect import _empty, Parameter, signature
import os


class SecurityError(ValueError):
    """Trying to do or access something that isn't allowed"""


class MagicMethods:
    possible_path_args = ['file', 'path']

    def __init__(self):
        self.methods = jsonrpcserver.methods.Methods()

    @staticmethod
    def is_safe_path(path):
        """
        Determines whether the file or path is within the current working directory
        :param str|PathLike path:
        :return: bool
        """
        return os.path.abspath(path).startswith(os.path.abspath(os.getcwd()))

    def serve(self, config, callback):
        """
        Responsible for creating a callback with proper documentation and arguments
        signature that can be registered as an api call.

        :param config:
        :param callback:
        :return: callable
        """
        cls = config.cls

        @wraps(cls)
        def _(*args, **kwargs):
            # only allow files from cwd to be used...
            try:
                # todo (?) add available files and folders as select options
                for name in self.possible_path_args:
                    if name in kwargs:
                        if not self.is_safe_path(kwargs[name]):
                            raise SecurityError("Access to unallowed file attempted", name)
            except SecurityError as e:
                data = {
                    "message": e.args[0],
                    "field": e.args[1]
                }
                raise AssertionError(json.dumps(data))

            result = callback(cls, *args, **kwargs)
            if isinstance(result, tuple) and hasattr(result, '_asdict'):
                result = result._asdict()
            return result

        # copy signature from original
        sig = signature(cls)

        def param_filter(param):
            return param.kind not in (Parameter.VAR_KEYWORD, Parameter.VAR_POSITIONAL)

        cb_params = signature(callback).parameters.values()
        cb_params = list(filter(param_filter, cb_params))

        extra_params = [parameter for parameter in cb_params
                        if parameter.name != 'cls']

        if len(extra_params):
            params = list(filter(lambda x: x.default is _empty, extra_params))
            params.extend(filter(param_filter, sig.parameters.values()))
            params.extend(list(filter(lambda x: x.default is not _empty, extra_params)))

        sig = sig.replace(parameters=params)

        _.__doc__ += callback.__doc__
        _.__signature__ = sig
        return _

    def load(self, name, module):
        """
        Load all possible callbacks for a given module

        :param str name:
        :param Module module:
        """
        factory = module.factory
        callables = list(factory)

        def lister():
            """
            Get a list of available core %s

            :return object: With key being the %s name, and value its description
            """
            return {config.name: config.docs for config in callables}

        lister.__doc__ = lister.__doc__ % (name, name)

        self.register("list.%s" % (name,), lister)

        # add each callable as its own api call
        for conf in callables:
            apicallname = '%s.%s' % (name, conf.name,)
            self.register(apicallname, self.serve(conf, module.callback))

    def register(self, name, callback):
        """
        Register a callback as an api call
        :param str name:
        :param callable callback:
        """
        self.methods.add(**{name: callback})


class DefaultMethods:
    @staticmethod
    def version():
        """
        Get the version of benchmarkstt

        :return str: BenchmarkSTT version
        """
        return __meta__.__version__

    @staticmethod
    def help(methods):
        def _():
            """
            Returns available api methods

            :return object: With key being the method name, and value its description
            """
            return {name: format_docs(func.__doc__) for name, func in methods.items.items()}
        return _


def get_methods() -> jsonrpcserver.methods.Methods:
    """
    Returns the available JSON-RPC api methods

    :return: jsonrpcserver.methods.Methods
    """

    methods = MagicMethods()
    methods.register('version', DefaultMethods.version)
    for name, module in Modules('api'):
        methods.load(name, module)

    methods.register('help', DefaultMethods.help(methods.methods))
    return methods.methods
