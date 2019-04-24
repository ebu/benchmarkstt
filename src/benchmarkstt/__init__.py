"""
Package benchmarkstt
"""

from .__meta__ import __author__, __version__


class DeferredStr:
    """Simple helper class to defer the execution of formatting functions until it is needed"""

    def __init__(self, func):
        self._func = func

    def __str__(self):
        return self._func()

    def __repr__(self):
        return self.__str__()


class DeferredRepr:
    """Simple helper class to defer the execution of repr call until it is needed"""
    def __init__(self, val):
        self._val = val

    def __str__(self):
        return repr(self._val)

    def __repr__(self):
        return self.__str__()


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
