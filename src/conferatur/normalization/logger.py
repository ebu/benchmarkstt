import difflib
from conferatur import make_printable
import logging

normalize_logger = logging.getLogger('conferatur.normalize')
normalize_logger._settings = {"printable": True}
normalize_stack = []


def get_diff(a, b, printable=None, delete_format=None, insert_format=None, formats=None):
    cruncher = difflib.SequenceMatcher(None, a, b)

    if delete_format is None:
        delete_format = '\033[31m%s\033[0m'
    if insert_format is None:
        insert_format = '\033[32m%s\033[0m'

    if formats is None:
        formats = {
            'replace': delete_format + insert_format,
            'delete': delete_format + '%s',
            'insert': '%s' + insert_format,
            'equal': '%s',
        }

    if printable is True:
        p = make_printable
    elif printable in (None, False):
        def p(txt):
            return txt
    else:
        p = printable

    res = []
    for tag, alo, ahi, blo, bhi in cruncher.get_opcodes():
        a_ = p(a[alo:ahi])

        if tag == 'equal':
            res.append(formats['equal'] % (p(a[alo:ahi]),))
            continue

        b_ = p(b[blo:bhi])
        res.append(formats[tag] % (a_, b_))
    return ''.join(res)


def log(func):
    """
    Log decorator for normalization classes
    """

    def _(cls, text):
        normalize_stack.append(type(cls).__name__)

        result = func(cls, text)
        logger_ = normalize_logger.getChild('.'.join(normalize_stack))

        diffs = get_diff(text, result, **normalize_logger._settings)

        if text != result:
            logger_.info('%s', diffs)
        else:
            logger_.debug('NORMALIZED [NOCHANGE]')

        normalize_stack.pop()
        return result
    return _

