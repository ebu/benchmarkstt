import logging
import os
from benchmarkstt.diff.formatter import DiffFormatter
from collections import namedtuple
from collections import OrderedDict

NormalizedLogItem = namedtuple('NormalizedLogItem', ['stack', 'original', 'normalized'])


class Logger:
    title = None
    logger = logging.getLogger('benchmarkstt.normalize')
    logger.setLevel(logging.INFO)
    logger.propagate = False
    stack = []


class ListHandler(logging.StreamHandler):
    def __init__(self):
        self._logs = []
        super().__init__(os.devnull)

    def emit(self, record):
        msg = self.format(record)
        self._logs.append(msg)

    @property
    def logs(self):
        return self._logs

    def flush(self):
        result = self._logs
        self._logs = []
        return result


class DiffLoggingFormatterDialect:
    def format(self, title, stack, diff):
        raise NotImplementedError()


class DiffLoggingTextFormatterDialect(DiffLoggingFormatterDialect):
    def format(self, title, stack, diff):
        args = []
        if title is not None:
            args.append(title)
        elif Logger.title is not None:
            args.append(Logger.title)
        args.append('/'.join(stack))
        args.append(diff)
        return ': '.join(args)


class DiffLoggingDictFormatterDialect(DiffLoggingFormatterDialect):
    def format(self, title, stack, diff):
        return OrderedDict(title=title, stack=stack, diff=diff)


class DiffLoggingFormatter(logging.Formatter):
    diff_logging_formatter_dialects = {
        "text": DiffLoggingTextFormatterDialect,
        "dict": DiffLoggingDictFormatterDialect,
    }

    def __init__(self, dialect=None, diff_formatter_dialect=None, title=None, *args, **kwargs):
        self._title = title
        self._differ = DiffFormatter(dialect, *args, **kwargs)
        strict = False
        if diff_formatter_dialect is None:
            diff_formatter_dialect = dialect
        else:
            strict = True

        self._formatter_dialect = self.get_dialect(diff_formatter_dialect, strict)
        super().__init__()

    def format(self, record):
        item = record.msg
        if type(item) is NormalizedLogItem:
            diff = self._differ.diff(item.original, item.normalized)
            return self._formatter_dialect.format(self._title, item.stack, diff)
        return super().format(record)

    @classmethod
    def has_dialect(cls, dialect):
        return dialect in cls.diff_logging_formatter_dialects

    @classmethod
    def get_dialect(cls, dialect, strict=None):
        if dialect is None:
            dialect = 'text'

        if not cls.has_dialect(dialect):
            if strict:
                raise ValueError("Unknown diff formatter dialect", dialect)

            dialect = 'text'

        return cls.diff_logging_formatter_dialects[dialect]()


def log(func):
    """
    Log decorator for normalization classes
    """

    def _(cls, text):
        Logger.stack.append(repr(cls))

        result = func(cls, text)
        logger_ = Logger.logger

        if text != result:
            logger_.info(NormalizedLogItem(list(Logger.stack), text, result))

        Logger.stack.pop()
        return result
    return _


class LogCapturer:
    def __init__(self, *args, **kwargs):
        self.formatter_args = (args, kwargs)
        self.handler = None

    def __enter__(self):
        self.handler = ListHandler()
        self.handler.setFormatter(DiffLoggingFormatter(*self.formatter_args[0], **self.formatter_args[1]))
        Logger.logger.addHandler(self.handler)
        return self

    @property
    def logs(self):
        return list(self.handler.logs)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.handler.flush()
        Logger.logger.removeHandler(self.handler)
        self.handler = None
