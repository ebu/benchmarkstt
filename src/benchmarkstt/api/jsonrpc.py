"""
Make benchmarkstt available through a rudimentary JSON-RPC_ interface

.. warning::
    Only supported for Python versions 3.6 and above!

.. _JSON-RPC: https://www.jsonrpc.org

"""

import jsonrpcserver
import json
from benchmarkstt import __meta__
from benchmarkstt.normalization import factory as normalization_factory
from benchmarkstt.metrics import factory as metrics_factory
from benchmarkstt.normalization.logger import ListHandler, DiffLoggingFormatter, normalize_logger
from functools import wraps, partial
from benchmarkstt.docblock import format_docs
import inspect
import os
import benchmarkstt.csv as csv


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

            return callback(cls, *args, **kwargs)

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

    extra_params = [
        dict(name='text', annotation=str,
             description='The text to normalize'),
        dict(name='return_logs', annotation=bool, default=None,
             description='Return normalizer logs'),
    ]

    def normalization_callback(cls, text, *args, **kwargs):
        return_logs = False
        if 'return_logs' in kwargs:
            return_logs = bool(kwargs['return_logs'])
            del kwargs['return_logs']

        if return_logs:
            handler = ListHandler()
            handler.setFormatter(DiffLoggingFormatter(dialect='html'))
            normalize_logger.addHandler(handler)

        try:
            result = {
                "text": cls(*args, **kwargs).normalize(text)
            }
            if return_logs:
                logs = handler.flush()
                result['logs'] = []
                for log in logs:
                    result['logs'].append(dict(names=log[0], message=log[1]))
            return result
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
        finally:
            if return_logs:
                normalize_logger.removeHandler(handler)

    add_methods('normalization', normalization_factory, normalization_callback, extra_params)
    # add_methods('metrics', metrics_factory)

    def _help():
        """
        Returns available api methods

        :return object: With key being the method name, and value its description
        """

        return {name: format_docs(func.__doc__)
                for name, func in methods.items.items()}

    methods.add(help=_help)
    return methods
