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

    def __init__(self, text: str, pattern=r'[\n\t\s]+'):
        self._text = text
        self._re = re.compile('(%s)' % (pattern,))

    def __iter__(self):
        iterable = self._re.split(self._text)

        pos = 0
        length = len(iterable)

        while pos < length:
            raw = ''.join(iterable[pos:pos+2])
            if raw != '':  # skip possible empty splits (at the end)
                segmented_on = iterable[pos+1] if pos + 1 < length else None
                yield Item({"item": iterable[pos], "type": "word", "@raw": raw, "@segmentedOn": segmented_on})
            pos += 2
