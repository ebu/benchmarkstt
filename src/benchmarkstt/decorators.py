import logging
from benchmarkstt import DeferredStr


def log_call(logger: logging.Logger, log_level=None, result=None):
    """
    Decorator to log all calls to decorated function to a given logger

    >>> import logging, sys
    >>> logging.basicConfig(stream=sys.stdout, format='%(levelname)s:%(name)s: %(message)s')
    >>> logger = logging.getLogger('logger_name')
    >>> logger.setLevel(logging.DEBUG)
    >>> @log_call(logger, logging.WARNING)
    ... def test(*args, **kwargs):
    ...     return 'result'
    >>> test('arg1', arg2='someval', arg3='someotherval')
    WARNING:logger_name: CALL test('arg1', arg2='someval', arg3='someotherval')
    'result'
    >>> @log_call(logger, result=True)
    ... def test(*args, **kwargs):
    ...     return 'result'
    >>> test(arg2='someval', arg3='someotherval', arg4=None)
    DEBUG:logger_name: CALL test(arg2='someval', arg3='someotherval', arg4=None)
    DEBUG:logger_name: RESULT test = 'result'
    'result'
    """

    if log_level is None:
        log_level = logging.DEBUG

    def _log_call(func):
        nonlocal log_level, result

        def _(*args, **kwargs):
            nonlocal log_level, result
            logger.log(log_level, 'CALL %s(%s)',
                       func.__name__,
                       DeferredStr(lambda: ', '.join([repr(a) for a in args] +
                                                     [k + '=' + repr(v) for k, v in kwargs.items()])))
            result_ = func(*args, **kwargs)
            if result:
                logger.log(log_level, 'RESULT %s = %s', func.__name__, DeferredStr(lambda: repr(result_)))
            return result_
        return _
    return _log_call
