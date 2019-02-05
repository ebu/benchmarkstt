"""
Package conferatur
"""

from .__meta__ import __author__, __version__
from importlib import import_module
import textwrap

modules = ('normalisation', 'api')


def get_modules(sub_module=None):
    postfix = '' if sub_module is None else '.' + sub_module
    for module in modules:
        yield module, import_module('conferatur.%s%s' % (module, postfix))


def get_modules_dict(sub_module=None):
    return {module: cli for module, cli in get_modules(sub_module)}


