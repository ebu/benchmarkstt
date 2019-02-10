"""
Package conferatur
"""

from .__meta__ import __author__, __version__
from importlib import import_module
import textwrap

modules = ('normalization', 'api')


def get_modules(sub_module=None):
    postfix = '' if sub_module is None else '.' + sub_module
    for module in modules:
        yield module, import_module('conferatur.%s%s' % (module, postfix))


def get_modules_dict(sub_module=None):
    return {module: cli for module, cli in get_modules(sub_module)}


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
