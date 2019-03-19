"""
Default input formats

Each format class should be accessible as iterator, each iteration should return a Word, so the input format is
essentially usable and can be easily converted to a :py:class:`benchmarkstt.schema.Schema`
"""

import benchmarkstt.tokenization.core as tokenizers
from benchmarkstt.schema import Word


class PlainText:
    def __init__(self, text, tokenizer=None):
        if tokenizer is None:
            tokenizer = tokenizers.Simple
        self._text = text
        self._tokenizer = tokenizer

    def __iter__(self):
        for item in self._tokenizer(self._text):
            yield Word(text=item)
