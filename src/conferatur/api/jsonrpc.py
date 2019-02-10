"""
Make conferatur available through a rudimentary JSON-RPC_ interface

.. _JSON-RPC: https://www.jsonrpc.org

"""

import jsonrpcserver
import json
from conferatur import __meta__
from conferatur.normalization import available_normalizers, logger
from functools import wraps
from conferatur.docblock import format_docs
import inspect
import os
import conferatur.csv as csv
import queue
from logging.handlers import QueueHandler
from markupsafe import escape


def get_methods() -> jsonrpcserver.methods.Methods:
    """
    Returns the available JSON-RPC api methods

    :return: jsonrpcserver.methods.Methods
    """

    logger.init_logger()
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
    def list_normalizers():
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
        def _(text, return_logs=None, *args, **kwargs):
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

            if return_logs:
                log_queue = queue.Queue()
                handler = QueueHandler(log_queue)
                logger.normalize_logger.addHandler(handler)
                prev_settings = dict(**logger.normalize_logger._settings)
                logger.normalize_logger._settings = {
                    "printable": escape,
                    "delete_format": '<span class="delete">%s</span>',
                    "insert_format": '<span class="insert">%s</span>'
                }

            try:
                result = {
                    "text": cls(*args, **kwargs).normalize(text)
                }
                if return_logs:
                    logs = list(log_queue.queue)
                    result['logs'] = [{"name": log.name, "message": log.message} for log in logs]
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
                    logger.normalize_logger._settings = prev_settings
                    logger.normalize_logger.removeHandler(handler)

        # copy signature from original normalizer, and add text param
        sig = inspect.signature(cls)
        params = list()
        params.append(inspect.Parameter('text', kind=inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=str))
        params.extend(sig.parameters.values())
        params.append(inspect.Parameter('return_logs', kind=inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=bool,
                                        default=None))
        sig = sig.replace(parameters=params)
        _.__signature__ = sig
        _.__doc__ += '\n    :param str text: The text to normalize'
        _.__doc__ += '\n    :param bool return_logs: Return normalizer logs'

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

