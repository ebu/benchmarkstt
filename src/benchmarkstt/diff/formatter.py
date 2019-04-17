import logging
from benchmarkstt import make_printable
import difflib
from markupsafe import escape

logger = logging.getLogger(__name__)


class Dialect:
    preprocessor = None
    delete_format = '%s'
    insert_format = '%s'
    equal_format = '%s'
    replace_format = None

    @staticmethod
    def format(names, diff):
        raise NotImplementedError()


class CLIDiffDialect(Dialect):
    preprocessor = make_printable
    delete_format = '\033[31m%s\033[0m'
    insert_format = '\033[32m%s\033[0m'

    @staticmethod
    def format(names, diff):
        return '|'.join(names) + ': ' + diff


class UTF8Dialect(Dialect):
    preprocessor = make_printable

    @staticmethod
    def delete_format(txt):
        return ''.join(c + '\u0338' for c in txt)

    @staticmethod
    def insert_format(txt):
        return ''.join(c + '\u0359' for c in txt)

    @staticmethod
    def format(names, diff):
        return '|'.join(names) + ': ' + diff


class HTMLDiffDialect(Dialect):
    preprocessor = escape
    delete_format = '<span class="delete">%s</span>'
    insert_format = '<span class="insert">%s</span>'

    @staticmethod
    def format(names, diff):
        return names, diff


class DiffFormatter:
    diff_dialects = {
        "cli": CLIDiffDialect,
        "html": HTMLDiffDialect,
        "text": UTF8Dialect
    }

    def __init__(self, dialect=None):
        if dialect is None:
            dialect = 'text'
        if dialect not in self.diff_dialects:
            raise ValueError("Unknown diff dialect", dialect)
        self._dialect = self.diff_dialects[dialect]

    def format(self, record):
        return self._dialect.format(record.args[0], self.diff(record.args[1], record.args[2]))

    def diff(self, a, b, opcodes=None, preprocessor=None):
        dialect = self._dialect

        def format_string(formatting):
            def _(*args):
                return formatting % args
            return _

        formats = dict(insert=None, delete=None, equal=None, replace=None)

        for f in formats.keys():
            formatter = getattr(dialect, f + '_format')
            if type(formatter) is str:
                formats[f] = format_string(formatter)
            else:
                formats[f] = formatter

        if formats['replace'] is None:
            def _(deleted, inserted):
                return formats['delete'](deleted) + formats['insert'](inserted)
            formats['replace'] = _

        if preprocessor is not None:
            def _pre(txt):
                return dialect.preprocessor(preprocessor(txt))
        else:
            _pre = dialect.preprocessor
        if opcodes is None:
            opcodes = difflib.SequenceMatcher(None, a, b).get_opcodes()

        res = []
        for tag, alo, ahi, blo, bhi in opcodes:
            a_ = _pre(a[alo:ahi])

            if tag in ('equal', 'delete'):
                res.append(formats[tag](_pre(a[alo:ahi])))
                continue

            b_ = _pre(b[blo:bhi])
            if tag == 'insert':
                res.append(formats[tag](b_))
                continue

            res.append(formats[tag](a_, b_))
        return ''.join(res)


def format_diff(a, b, opcodes=None, dialect=None, preprocessor=None):
    formatter = DiffFormatter(dialect)
    return formatter.diff(a, b, opcodes, preprocessor)
