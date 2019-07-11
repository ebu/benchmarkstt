"""
Package benchmarkstt
"""

from .__meta__ import __author__, __version__
from functools import partial, wraps
from os import getenv


class DeferredCallback:
    """Simple helper class to defer the execution of formatting functions until it is needed"""

    def __init__(self, cb, *args, **kwargs):
        self._cb = wraps(cb)(partial(cb, *args, **kwargs))

    def __str__(self):
        return self._cb()

    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, repr(self._cb()))


class DeferredList:
    def __init__(self, cb):
        self._cb = cb
        self._list = None

    @property
    def list(self):
        if self._list is None:
            self._list = self._cb()
        return self._list

    def __getitem__(self, item):
        return self.list[item]


def make_printable(char):
    """
    Return printable representation of ascii/utf-8 control characters

    :param str char:
    :return str:
    """
    if not len(char):
        return ''
    if len(char) > 1:
        return ''.join(list(map(make_printable, char)))

    codepoint = ord(char)
    if 0x00 <= codepoint <= 0x1f or 0x7f <= codepoint <= 0x9f:
        return chr(0x2400 | codepoint)

    return char if char != ' ' else '·'


class _Settings:
    @property
    def default_encoding(self):
        return getenv('DEFAULT_ENCODING', 'UTF-8')


settings = _Settings()
