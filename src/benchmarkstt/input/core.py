"""
Default input formats

Each format class should be accessible as iterator, each iteration should return a Word, so the input format is
essentially usable and can be easily converted to a :py:class:`benchmarkstt.schema.Schema`
"""

import benchmarkstt.segmentation.core as segmenters
from benchmarkstt.schema import Word


class PlainText:
    def __init__(self, text, segmenter=None):
        if segmenter is None:
            segmenter = segmenters.Simple
        self._text = text
        self._segmenter = segmenter

    def __iter__(self):
        return iter(self._segmenter(self._text))
