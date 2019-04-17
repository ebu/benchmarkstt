"""
Core segmenters, each segmenter must be Iterable returning a Item
"""

import re
from benchmarkstt.schema import Item
from benchmarkstt.segmentation import Base


class Simple(Base):
    """
    Simplest case, split into words by white space
    """

    def __init__(self, text: str, pattern=r'[\n\t\s]+', normalizer=None):
        self._text = text
        self._re = re.compile('(%s)' % (pattern,))
        self._normalizer = normalizer
        if self._normalizer is not None:
            self._text = self._normalizer.normalize(text)

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
            yield Item({"item": matches[1], "type": "word", "@raw": ''.join(matches)})

        while pos < length:
            raw = ''.join(iterable[pos:pos+2])
            if raw != '':
                yield Item({"item": iterable[pos], "type": "word", "@raw": raw})
            pos += 2
