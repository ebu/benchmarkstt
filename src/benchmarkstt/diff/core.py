"""
Core Diff algorithms
"""

from difflib import SequenceMatcher
from benchmarkstt.diff import Differ
import edit_distance
import editdistance


class RatcliffObershelp(Differ):
    """
    Diff according to Ratcliff and Obershelp (Gestalt) matching algorithm.

    From difflib.SequenceMatcher_ (Copyright_ 2001-2020, Python Software Foundation.)

        The basic algorithm predates, and is a little fancier than, an algorithm
        published in the late 1980's by Ratcliff and Obershelp under the
        hyperbolic name "gestalt pattern matching".  The basic idea is to find
        the longest contiguous matching subsequence that contains no "junk"
        elements (R-O doesn't address junk).  The same idea is then applied
        recursively to the pieces of the sequences to the left and to the right
        of the matching subsequence.  This does not yield minimal edit
        sequences, but does tend to yield matches that "look right" to people.

     .. _Copyright: https://docs.python.org/3.8/copyright.html
     .. _difflib.SequenceMatcher: https://docs.python.org/3.8/library/difflib.html
     .. _DrDobbs: https://www.drdobbs.com/database/pattern-matching-the-gestalt-approach/184407970
    """

    def __init__(self, a, b, **kwargs):
        kwargs['a'] = a
        kwargs['b'] = b
        self._kwargs = kwargs
        self._matcher = SequenceMatcher(**self._kwargs)

    def get_opcodes(self):
        return self._matcher.get_opcodes()


class Levenshtein(Differ):
    """
    Levenshtein_ distance is the minimum edit distance.

    .. _Levenshtein: https://en.wikipedia.org/wiki/Levenshtein_distance
    """

    def __init__(self, a, b, **kwargs):
        kwargs['a'] = a
        kwargs['b'] = b
        if 'action_function' not in kwargs:
            kwargs['action_function'] = edit_distance.highest_match_action
        self._kwargs = kwargs
        self._matcher = edit_distance.SequenceMatcher(**self._kwargs)

    def get_opcodes(self):
        return self.simplify_opcodes(self._matcher.get_opcodes())

    def get_error_rate(self):
        a = self._kwargs['a']
        b = self._kwargs['b']
        return editdistance.eval(a, b) / len(a)

    @staticmethod
    def simplify_opcodes(opcodes):
        new_codes = []
        prev = None
        for cur in opcodes:
            if prev is None:
                prev = cur
            elif cur[0] == prev[0]:
                prev[2] = cur[2]
                prev[4] = cur[4]
            else:
                new_codes.append(tuple(prev))
                prev = cur

        if prev is not None:
            new_codes.append(tuple(prev))

        return new_codes
