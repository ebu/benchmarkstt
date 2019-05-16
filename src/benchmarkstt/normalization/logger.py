import logging
import os
from benchmarkstt.diff.formatter import DiffFormatter

normalize_logger = logging.getLogger('benchmarkstt.normalize')
normalize_logger.setLevel(logging.INFO)
normalize_logger.propagate = False
normalize_stack = []


class ListHandler(logging.StreamHandler):
    def __init__(self):
        self._logs = []
        super().__init__(os.devnull)

    def emit(self, record):
        msg = self.format(record)
        self._logs.append(msg)

    def flush(self):
        result = self._logs
        self._logs = []
        return result


class DiffLoggingFormatter(logging.Formatter):
    def __init__(self, dialect=None):
        self._differ = DiffFormatter(dialect)
        super().__init__()

    def format(self, record):
        return self._differ.format(record)


def log(func):
    """
    Log decorator for normalization classes
    """

    def _(cls, text):
        normalize_stack.append(repr(cls)) # type(cls).__name__)

        result = func(cls, text)
        logger_ = normalize_logger

        if text != result:
            logger_.info('%s: %s -> %s', list(normalize_stack), text, result)
        else:
            logger_.debug('NORMALIZED [NOCHANGE]')

        normalize_stack.pop()
        return result
    return _
