import logging
from benchmarkstt import make_printable
import difflib
from markupsafe import escape
from benchmarkstt.schema import Schema
from io import StringIO
from collections import OrderedDict

logger = logging.getLogger(__name__)


class Dialect:
    preprocessor = None
    delete_format = '%s'
    insert_format = '%s'
    equal_format = '%s'
    replace_format = None

    def __init__(self):
        self._stream = StringIO()

    @property
    def stream(self):
        return self._stream

    def __enter__(self):
        self._stream = StringIO()
        return self._stream

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def output(self):
        return self._stream.getvalue()


class CLIDiffDialect(Dialect):
    @staticmethod
    def preprocessor(txt):
        return make_printable(txt)

    delete_format = '\033[31m%s\033[0m'
    insert_format = '\033[32m%s\033[0m'


class UTF8Dialect(Dialect):
    @staticmethod
    def preprocessor(txt):
        return make_printable(txt)

    def delete_format(self, txt):
        self._stream.writelines(c + '\u0338' for c in txt)

    def insert_format(self, txt):
        self._stream.writelines(c + '\u0359' for c in txt)


class HTMLDiffDialect(Dialect):
    @staticmethod
    def preprocessor(txt):
        return escape(txt)

    delete_format = '<span class="delete">%s</span>'
    insert_format = '<span class="insert">%s</span>'


class ListDialect(Dialect):
    @staticmethod
    def preprocessor(txt):
        return txt

    def delete_format(self, txt):
        return self._format('delete', txt)

    def insert_format(self, txt):
        return self._format('insert', txt)

    def equal_format(self, txt):
        return self._format('equal', txt)

    def replace_format(self, a, b):
        return self._format('replace', a, b)

    def _format(self, kind, txt, txt2=None):
        txt = txt.split()
        if txt2 is None:
            txt2 = txt
        else:
            txt2 = txt2.split()

        oor = len(txt2)
        for idx, word in enumerate(txt):
            ref = word if kind != 'insert' else None
            if idx >= oor:
                kind = 'delete'
            hyp = txt2[idx] if kind != 'delete' else None
            result = OrderedDict((('kind', kind), ('reference', ref), ('hypothesis', hyp)))
            self._output.append(result)

        if idx < oor:
            for word_ in txt2[idx+1:]:
                result = OrderedDict((('kind', 'insert'), ('reference', None), ('hypothesis', word_)))
                self._output.append(result)

    def __enter__(self):
        self._output = []
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def output(self):
        return self._output


class JSONDiffDialect(ListDialect):
    def __init__(self):
        self._line = None

    def __enter__(self):
        super().__enter__()
        self._stream = StringIO()
        self._line = 0
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self._line = None
        self._stream.write(Schema.dumps(super().output()))

    def output(self):
        return self._stream.getvalue()


class DiffFormatter:
    diff_dialects = {
        "cli": CLIDiffDialect,
        "html": HTMLDiffDialect,
        "text": UTF8Dialect,
        "json": JSONDiffDialect,
        "list": ListDialect,
    }

    def __init__(self, dialect=None):
        if dialect is None:
            dialect = 'text'

        if not self.has_dialect(dialect):
            raise ValueError("Unknown diff dialect", dialect)
        self._dialect = self.diff_dialects[dialect]()

    def diff(self, a, b, opcodes=None, preprocessor=None):
        formats = dict(insert=None, delete=None, equal=None, replace=None)

        dialect = self._dialect
        with dialect as stream:
            def format_string(formatting):
                def _(*args):
                    dialect.stream.write(formatting % args)

                return _

            # dialect = self._dialect
            for f in formats.keys():
                formatter = getattr(dialect, f + '_format')
                if type(formatter) is str:
                    formats[f] = format_string(formatter)
                else:
                    formats[f] = formatter

            if formats['replace'] is None:
                def _(deleted, inserted):
                    formats['delete'](deleted)
                    formats['insert'](inserted)
                formats['replace'] = _

            if preprocessor is not None:
                def _pre(txt):
                    return dialect.preprocessor(preprocessor(txt))
            else:
                _pre = dialect.preprocessor

            if opcodes is None:
                opcodes = difflib.SequenceMatcher(None, a, b).get_opcodes()

            for tag, alo, ahi, blo, bhi in opcodes:
                a_ = _pre(a[alo:ahi])

                if tag in ('equal', 'delete'):
                    formats[tag](_pre(a[alo:ahi]))
                else:
                    b_ = _pre(b[blo:bhi])
                    if tag == 'insert':
                        formats[tag](b_)
                    else:
                        formats[tag](a_, b_)
        return dialect.output()

    @classmethod
    def has_dialect(cls, dialect):
        return dialect in cls.diff_dialects


def format_diff(a, b, opcodes=None, dialect=None, preprocessor=None):
    formatter = DiffFormatter(dialect)
    return formatter.diff(a, b, opcodes, preprocessor)
