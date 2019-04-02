"""
Core segmenters, each segmenter must be Iterable returning a Word
"""

import re
from benchmarkstt.schema import Word


class Simple:
    """
    Simplest case, split into words by white space
    """

    def __init__(self, text: str, pattern=r'[\n\t\s]+'):
        self._text = text
        self._re = re.compile('(%s)' % (pattern,))

    def __iter__(self):
        start_match = self._re.match(self._text)
        iterable = self._re.split(self._text)
        if iterable[0] == '':
            iterable.pop(0)

        pos = 0
        length = len(iterable)

        # special case, starts with word break, add it to first word
        if start_match is not None:
            matches = iterable[0:3]
            pos = 3
            yield Word({"item": matches[1], "type": "word", "@raw": ''.join(matches)})

        while pos < length:
            raw = ''.join(iterable[pos:pos+2])
            if raw != '':
                yield Word({"item": iterable[pos], "type": "word", "@raw": raw})
            pos += 2
