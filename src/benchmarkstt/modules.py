import sys
from importlib import import_module

_modules = ['normalization', 'metrics', 'flow']

if sys.version_info >= (3, 6):
    _modules.append('api')


class Modules:
    def __init__(self, sub_module):
        self._postfix = '' if sub_module is None else '.' + sub_module

    def __iter__(self):
        for module in _modules:
            try:
                yield (module, self[module])
            except IndexError:
                pass

    def __getattr__(self, name):
        return self[name]

    def __getitem__(self, key):
        name = 'benchmarkstt.%s%s' % (key, self._postfix)
        try:
            return import_module(name)
        except ImportError:
            raise IndexError('Module not found', key)

    def keys(self):
        return [key for key, value in iter(self)]
