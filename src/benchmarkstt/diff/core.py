"""
Core Diff algorithms
"""

from difflib import SequenceMatcher
from benchmarkstt.diff import Differ


class RatcliffObershelp(Differ):
    """
    Diff according to Ratcliff and Obershelp (Gestalt) matching algorithm.

    From difflib.SequenceMatcher_ (Copyright_ 2001-2020, Python Software Foundation.)

        SequenceMatcher is a flexible class for comparing pairs of sequences of
        any type, so long as the sequence elements are hashable.  The basic
        algorithm predates, and is a little fancier than, an algorithm
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
        if 'autojunk' not in kwargs:
            kwargs['autojunk'] = False
        kwargs['a'] = a
        kwargs['b'] = b
        self.matcher = SequenceMatcher(**kwargs)

    def get_opcodes(self):
        return self.matcher.get_opcodes()
