"""
Responsible for calculating differences.
"""

from abc import ABC, ABCMeta, abstractmethod
from benchmarkstt.factory import CoreFactory
from collections import namedtuple


OpcodeCounts = namedtuple('OpcodeCounts',
                          ('equal', 'replace', 'insert', 'delete'))


def get_opcode_counts(opcodes) -> OpcodeCounts:
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


class DifferInterface(ABC):
    @abstractmethod
    def __init__(self, a, b):
        """
        :meta public:
        """
        raise NotImplementedError()

    @abstractmethod
    def get_opcodes(self):
        """
        Return list of 5-tuples describing how to turn `a` into `b`.

        Each tuple is of the form `(tag, i1, i2, j1, j2)`. The first tuple has
        `i1 == j1 == 0`, and remaining tuples have `i1` equals the `i2` from the
        tuple preceding it, and likewise for `j1` equals the previous `j2`.

        The tags are strings, with these meanings:

         - 'replace': `a[i1:i2]` should be replaced by `b[j1:j2]`
         - 'delete': `a[i1:i2]` should be deleted. Note that `j1==j2` in this case.
         - 'insert': `b[j1:j2]` should be inserted at `a[i1:i1]`. Note that `i1==i2` in this case.
         - 'equal': `a[i1:i2] == b[j1:j2]`
        """
        raise NotImplementedError()

    @abstractmethod
    def get_opcode_counts(self):
        raise NotImplementedError()

    @abstractmethod
    def get_error_rate(self):
        raise NotImplementedError()


class Differ(DifferInterface, metaclass=ABCMeta):
    def get_opcode_counts(self):
        return get_opcode_counts(self.get_opcodes())

    def get_error_rate(self):
        counts = self.get_opcode_counts()

        changes = counts.replace + counts.delete + counts.insert
        total = counts.equal + counts.replace + counts.delete

        return changes / total


factory = CoreFactory(DifferInterface, False)
