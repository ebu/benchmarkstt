from benchmarkstt.schema import Schema
import logging
from benchmarkstt.diff.core import RatcliffObershelp
from benchmarkstt.diff.formatter import format_diff
from benchmarkstt.metrics import Base
from collections import namedtuple
# from benchmarkstt.modules import LoadObjectProxy
import editdistance

logger = logging.getLogger(__name__)

OpcodeCounts = namedtuple('OpcodeCounts',
                          ('equal', 'replace', 'insert', 'delete'))


def traversible(schema, key=None):
    if key is None:
        key = 'item'
    return [word[key] for word in schema]


def get_opcode_counts(opcodes):
    counts = OpcodeCounts(0, 0, 0, 0)._asdict()
    for tag, alo, ahi, blo, bhi in opcodes:
        if tag == 'equal':
            counts[tag] += ahi - alo
        elif tag == 'insert':
            counts[tag] += bhi - blo
        elif tag == 'delete':
            counts[tag] += ahi - alo
        elif tag == 'replace':
            ca = ahi - alo
            cb = bhi - blo
            if ca < cb:
                counts['insert'] += cb - ca
                counts['replace'] += ca
            elif ca > cb:
                counts['delete'] += ca - cb
                counts['replace'] += cb
            else:
                counts[tag] += ahi - alo
    return OpcodeCounts(counts['equal'], counts['replace'], counts['insert'], counts['delete'])


def get_differ(a, b, differ_class):
    if differ_class is None:
        # differ_class = HuntMcIlroy
        differ_class = RatcliffObershelp
    return differ_class(traversible(a), traversible(b))


class WordDiffs(Base):
    """
    Present differences on a per-word basis

    :param dialect: Presentation format. Default is 'cli'.
    :example dialect: 'html'
    :param differ_class: For future use.
    """

    def __init__(self, dialect=None, differ_class=None):
        self._differ_class = differ_class
        self._dialect = dialect

    def compare(self, ref: Schema, hyp: Schema):
        differ = get_differ(ref, hyp, differ_class=self._differ_class)
        a = traversible(ref)
        b = traversible(hyp)
        return format_diff(a, b, differ.get_opcodes(),
                           dialect=self._dialect,
                           preprocessor=lambda x: ' %s' % (' '.join(x),))


class WER(Base):
    """
    Word Error Rate, basically defined as::

        insertions + deletions + substitions
        ------------------------------------
             number of reference words

    See: https://en.wikipedia.org/wiki/Word_error_rate

    Calculates the WER using one of two algorithms:

    [Mode: 'strict' or 'hunt'] Insertions, deletions and
    substitutions are identified using the Hunt–McIlroy
    diff algorithm. The 'hunt' mode applies 0.5 weight to
    insertions and deletions. This algorithm is the one
    used internally by Python.
    See https://docs.python.org/3/library/difflib.html

    [Mode: 'levenshtein'] In the context of WER, Levenshtein
    distance is the minimum edit distance computed at the
    word level. This implementation uses the Editdistance
    c++ implementation by Hiroyuki Tanaka:
    https://github.com/aflc/editdistance. See:
    https://en.wikipedia.org/wiki/Levenshtein_distance

    :param mode: 'strict' (default), 'hunt' or 'levenshtein'.
    :param differ_class: For future use.
    """

    # WER modes
    MODE_STRICT = 'strict'
    MODE_HUNT = 'hunt'
    MODE_LEVENSHTEIN = 'levenshtein'

    DEL_PENALTY = 1
    INS_PENALTY = 1
    SUB_PENALTY = 1

    def __init__(self, mode=None, differ_class=None):
        self._mode = mode
        if mode == self.MODE_LEVENSHTEIN:
            return

        if differ_class is None:
            differ_class = RatcliffObershelp
        self._differ_class = differ_class
        if mode == self.MODE_HUNT:
            self.DEL_PENALTY = self.INS_PENALTY = .5

    def compare(self, ref: Schema, hyp: Schema):
        if self._mode == self.MODE_LEVENSHTEIN:
            ref_list = [i['item'] for i in ref]
            total_ref = len(ref_list)
            if total_ref == 0:
                return 1
            return editdistance.eval(ref_list, [i['item'] for i in hyp]) / total_ref

        diffs = get_differ(ref, hyp, differ_class=self._differ_class)

        counts = get_opcode_counts(diffs.get_opcodes())

        changes = counts.replace * self.SUB_PENALTY + \
            counts.delete * self.DEL_PENALTY + \
            counts.insert * self.INS_PENALTY

        total_ref = counts.equal + counts.replace + counts.delete
        if total_ref == 0:
            return 1
        return changes / total_ref


class DiffCounts(Base):
    """
    Get the amount of differences between reference and hypothesis
    """

    def __init__(self, differ_class=None):
        if differ_class is None:
            differ_class = RatcliffObershelp
        self._differ_class = differ_class

    def compare(self, ref: Schema, hyp: Schema):
        diffs = get_differ(ref, hyp, differ_class=self._differ_class)
        return get_opcode_counts(diffs.get_opcodes())


# For a future version
# class ExternalMetric(LoadObjectProxy, Base):
#     """
#     Automatically loads an external metric class.
#
#     :param name: The name of the metric to load (eg. mymodule.metrics.MyOwnMetricClass)
#     """
