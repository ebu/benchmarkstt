"""
Make benchmarkstt available through a rudimentary JSON-RPC_ interface

.. warning::
    Only supported for Python versions 3.6 and above!

.. _JSON-RPC: https://www.jsonrpc.org

"""

import jsonrpcserver
import json
from benchmarkstt import __meta__
from functools import wraps, partial
from benchmarkstt.docblock import format_docs
from benchmarkstt.modules import Modules
import inspect
import os


def add_methods_from_module(methods, name, factory, callback, extra_params=None):
    def is_safe_path(path):
        """
        Determines whether the file or path is within the current working directory
        :param str|PathLike path:
        :return: bool
        """
        return os.path.abspath(path).startswith(os.path.abspath(os.getcwd()))

    class SecurityError(ValueError):
        """Trying to do or access something that isn't allowed"""

    callables = list(factory)

    def serve(config):
        cls = config.cls

        @wraps(cls)
        def _(*args, **kwargs):
            # only allow files from cwd to be used...
            try:
                if 'file' in kwargs:
                    if not is_safe_path(kwargs['file']):
                        raise SecurityError("Access to unallowed file attempted", 'file')

                if 'path' in kwargs:
                    if not is_safe_path(kwargs['path']):
                        raise SecurityError("Access to unallowed directory attempted", 'path')

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

        # copy signature from original, add params
        sig = inspect.signature(cls)
        if extra_params:
            def mapper(param_settings):
                kwargs = dict(**param_settings,
                              kind=inspect.Parameter.POSITIONAL_OR_KEYWORD)
                del kwargs['description']
                return inspect.Parameter(**kwargs)

            mapper = partial(map, mapper)
            params = list(mapper(filter(lambda x: 'default' not in x, extra_params)))
            params.extend(sig.parameters.values())
            params.extend(list(mapper(filter(lambda x: 'default' in x, extra_params))))
            sig = sig.replace(parameters=params)

            for param in extra_params:
                _.__doc__ += '\n    :param %s %s: %s' % (param['annotation'].__name__,
                                                         param['name'],
                                                         param['description'])

        _.__signature__ = sig

        # todo (?) add available files and folders as select options
        return _

    def lister():
        """
        Get a list of available core %s

        :return object: With key being the %s name, and value its description
        """
        return {config.name: config.docs for config in callables}

    lister.__doc__ = lister.__doc__ % (name, name)

    methods.add(**{"list.%s" % (name,): lister})

    # add each normalizer as its own api call
    for conf in callables:
        apicallname = '%s.%s' % (name, conf.name,)
        methods.add(**{apicallname: serve(conf)})


def get_methods() -> jsonrpcserver.methods.Methods:
    """
    Returns the available JSON-RPC api methods

    :return: jsonrpcserver.methods.Methods
    """

    methods = jsonrpcserver.methods.Methods()
    add_methods = partial(add_methods_from_module, methods)

    def version():
        """
        Get the version of benchmarkstt

        :return str: BenchmarkSTT version
        """

        return __meta__.__version__

    methods.add(version=version)

    for name, module in Modules('api'):
        add_methods(name, module.factory, module.callback, module.extra_params)

    def _help():
        """
        Returns available api methods

        :return object: With key being the method name, and value its description
        """

        return {name: format_docs(func.__doc__)
                for name, func in methods.items.items()}

    methods.add(help=_help)
    return methods
