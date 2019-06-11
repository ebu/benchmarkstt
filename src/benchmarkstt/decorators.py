import logging
from benchmarkstt import DeferredCallback


def log_call(logger: logging.Logger, log_level=None, result=None):
    """
    Decorator to log all calls to decorated function to given logger

    >>> import logging, sys, io
    >>>
    >>> logger = logging.getLogger('logger_name')
    >>> logger.setLevel(logging.DEBUG)
    >>> ch = logging.StreamHandler(sys.stdout)
    >>> ch.setFormatter(logging.Formatter('%(levelname)s:%(name)s: %(message)s'))
    >>> logger.addHandler(ch)
    >>>
    >>> @log_call(logger, logging.WARNING)
    ... def test(*args, **kwargs):
    ...     return 'result'
    >>> test('arg1', arg2='someval', arg3='someotherval')
    WARNING:logger_name: test('arg1', arg2='someval', arg3='someotherval')
    'result'
    >>> @log_call(logger, result=True)
    ... def test(*args, **kwargs):
    ...     return 'result'
    >>> test(arg2='someval', arg3='someotherval')
    DEBUG:logger_name: test(arg2='someval', arg3='someotherval')
    DEBUG:logger_name: test returned: result
    'result'
    """

    if log_level is None:
        log_level = logging.DEBUG

    def _log_call(func: callable):
        def _(*args, **kwargs):
            arguments_format = []
            arguments_list = []
            if len(args):
                arguments_format.append('%s')
                arguments_list.append(DeferredCallback(lambda: ', '.join([repr(a) for a in args])))
            if len(kwargs):
                arguments_format.append('%s')
                arguments_list.append(DeferredCallback(lambda: ', '.join([k + '=' + repr(kwargs[k]) for k in kwargs])))

            arguments_format = '%s(%s)' % (func.__name__, ', '.join(arguments_format))

            logger.log(log_level, arguments_format, *arguments_list)
            result_ = func(*args, **kwargs)
            if result:
                logger.log(log_level, '%s returned: %s', func.__name__, result_)
            return result_
        return _
    return _log_call
