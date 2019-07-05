import logging
import os
from benchmarkstt.diff.formatter import DiffFormatter
from collections import namedtuple

normalize_logger = logging.getLogger('benchmarkstt.normalize')
normalize_logger.setLevel(logging.INFO)
normalize_logger.propagate = False
normalize_stack = []


NormalizedLogItem = namedtuple('NormalizedLogItem', ['stack', 'original', 'normalized'])


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
        return ': '.join(['/'.join(stack), diff])


class DiffLoggingJsonFormatterDialect(DiffLoggingFormatterDialect):
    def format(self, title, stack, diff):
        # todo: json formatter
        return DiffLoggingTextFormatterDialect().format(title, stack, diff)


class DiffLoggingFormatter(logging.Formatter):
    diff_logging_formatter_dialects = {
        "text": DiffLoggingTextFormatterDialect,
        "json": DiffLoggingJsonFormatterDialect,
    }

    def __init__(self, dialect=None, diff_formatter_dialect=None):
        self._differ = DiffFormatter(dialect)
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
            return self._formatter_dialect.format(None, item.stack, diff)
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
        normalize_stack.append(repr(cls))

        result = func(cls, text)
        logger_ = normalize_logger

        if text != result:
            logger_.info(NormalizedLogItem(normalize_stack, text, result))

        normalize_stack.pop()
        return result
    return _


class LogCapturer:
    def __init__(self, dialect=None):
        self.dialect = dialect
        self.handler = None

    def __enter__(self):
        self.handler = ListHandler()
        self.handler.setFormatter(DiffLoggingFormatter(dialect=self.dialect))
        normalize_logger.addHandler(self.handler)
        return self

    @property
    def logs(self):
        return [dict(names=log_[0], message=log_[1]) for log_ in self.handler.logs]

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.handler.flush()
        normalize_logger.removeHandler(self.handler)
        self.handler = None
