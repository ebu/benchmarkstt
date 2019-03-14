"""
Core tokenizers, each tokenizer must be Iterable
"""


class Simple:
    def __init__(self, text):
        self._text = text

    def __iter__(self):
        return iter(self._text.split())
