import logging
from benchmarkstt import make_printable
import difflib
from markupsafe import escape

logger = logging.getLogger(__name__)


class CLIDiffDialect:
    preprocessor = make_printable
    preprocessor = lambda x: x
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


class DiffFormatter:
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

    def diff(self, a, b, opcodes=None, preprocessor=None):
        dialect = self._dialect
        if preprocessor is not None:
            def _pre(a):
                return dialect.preprocessor(preprocessor(a))
        else:
            _pre = dialect.preprocessor
        if opcodes is None:
            opcodes = difflib.SequenceMatcher(None, a, b).get_opcodes()

        if dialect.formats is None:
            formats = {
                'replace': dialect.delete_format + dialect.insert_format,
                'delete': dialect.delete_format + '%s',
                'insert': '%s' + dialect.insert_format,
                'equal': '%s',
            }

        res = []
        for tag, alo, ahi, blo, bhi in opcodes:
            a_ = _pre(a[alo:ahi])

            if tag == 'equal':
                res.append(formats['equal'] % (_pre(a[alo:ahi]),))
                continue

            b_ = _pre(b[blo:bhi])
            res.append(formats[tag] % (a_, b_))
        return ''.join(res)


def format_diff(a, b, opcodes=None, dialect=None, preprocessor=None):
    formatter = DiffFormatter(dialect)
    return formatter.diff(a, b, opcodes, preprocessor=preprocessor)

