import difflib
from conferatur import make_printable
import logging
from markupsafe import escape
import os
from conferatur import DeferredRepr

normalize_logger = logging.getLogger('conferatur.normalize')
normalize_logger.setLevel(logging.INFO)
normalize_logger.propagate = False
normalize_stack = []


class CLIDiffDialect:
    preprocessor = make_printable
    delete_format = '\033[31m%s\033[0m'
    insert_format = '\033[32m%s\033[0m'
    formats = None

    @staticmethod
    def format(names, diff):
        return '|'.join(names) + ': ' + diff


class HTMLDiffDialect:
    preprocessor = escape
    delete_format = '<span class="delete">%s</span>'
    insert_format = '<span class="insert">%s</span>'
    formats = None

    @staticmethod
    def format(names, diff):
        return names, diff


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
        self._differ = Differ(dialect)
        super().__init__()

    def format(self, record):
        return self._differ.format(record)


class Differ:
    diff_dialects = {
        "cli": CLIDiffDialect,
        "html": HTMLDiffDialect
    }

    def __init__(self, dialect=None):
        if dialect is None:
            dialect = 'cli'
        if dialect not in self.diff_dialects:
            raise ValueError("Unknown diff dialect", dialect)
        self._dialect = self.diff_dialects[dialect]

    def format(self, record):
        return self._dialect.format(record.args[0], self.diff(record.args[1], record.args[2]))

    def diff(self, a, b):
        dialect = self._dialect
        preprocessor = dialect.preprocessor
        cruncher = difflib.SequenceMatcher(None, a, b)

        if dialect.formats is None:
            formats = {
                'replace': dialect.delete_format + dialect.insert_format,
                'delete': dialect.delete_format + '%s',
                'insert': '%s' + dialect.insert_format,
                'equal': '%s',
            }

        res = []
        for tag, alo, ahi, blo, bhi in cruncher.get_opcodes():
            a_ = preprocessor(a[alo:ahi])

            if tag == 'equal':
                res.append(formats['equal'] % (preprocessor(a[alo:ahi]),))
                continue

            b_ = preprocessor(b[blo:bhi])
            res.append(formats[tag] % (a_, b_))
        return ''.join(res)


def log(func):
    """
    Log decorator for normalization classes
    """

    def _(cls, text):
        normalize_stack.append(type(cls).__name__)

        result = func(cls, text)
        logger_ = normalize_logger

        if text != result:
            logger_.info('%s: %s -> %s', list(normalize_stack), text, result)
        else:
            logger_.debug('NORMALIZED [NOCHANGE]')

        normalize_stack.pop()
        return result
    return _
