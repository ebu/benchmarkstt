import sys
import logging
from importlib import import_module

_modules = ['normalization', 'metrics', 'benchmark']

logger = logging.getLogger(__name__)

if sys.version_info >= (3, 6):
    # only supported in python >= 3.6
    _modules.append('api')


class HiddenModuleError(Exception):
    pass


class Modules:
    def __init__(self, sub_module=None):
        self._submodule = '' if sub_module is None else sub_module

    def __iter__(self):
        for module in _modules:
            try:
                yield module, self._import(module)
            except HiddenModuleError as e:
                logger.debug("Hidden module skipped: %s", e)
            except ImportError as e:
                logger.warning("Could not import benchmarkstt.%s.entrypoints.%s: %s", self._submodule, module, e)

    def __getattr__(self, name):
        return self[name]

    def __getitem__(self, key):
        try:
            return self._import(key)
        except ImportError:
            raise IndexError('Module not found', key)
        except HiddenModuleError:
            raise IndexError('Module is hidden', key)

    def keys(self):
        return [key for key, value in iter(self)]

    def _import(self, key):
        name = 'benchmarkstt.%s.entrypoints.%s' % (self._submodule, key)
        module = import_module(name)

        if hasattr(module, 'hidden'):
            if module.hidden:
                raise HiddenModuleError(name)
        return module


def load_object(name, transform=None):
    """
    Load an object based on a string.

    :param name: The string representation of an object
    :param transform: Transform (callable) done on the object name for comparison, if None, will lowercase compare.
                      False for no transform.
    """
    module = list(name.split('.'))

    if transform is None:
        transform = str.lower
    elif transform is False:
        def identity(x):
            return x
        transform = identity

    class_name = transform(module.pop())

    if not len(module):
        raise ImportError("Could not find an object for %r" % (name,))

    module = '.'.join(module)

    module = import_module(module)

    for found_class_name in dir(module):
        if transform(found_class_name) != class_name:
            continue
        return getattr(module, found_class_name)

    raise ImportError("Could not find an object for %r" % (name,))
