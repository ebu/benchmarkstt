import sys
from importlib import import_module

_modules = ['normalization', 'metrics', 'benchmark']

if sys.version_info >= (3, 6):
    # only supported in python >= 3.6
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
            module = import_module(name)
            if hasattr(module, 'hidden'):
                if module.hidden:
                    raise ImportError()
            return module
        except ImportError:
            raise IndexError('Module not found', key)

    def keys(self):
        return [key for key, value in iter(self)]


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
    module = '.'.join(module)
    if len(module) == 0:
        module = globals()
    else:
        module = import_module(module)

    for found_class_name in dir(module):
        if transform(found_class_name) != class_name:
            continue
        return getattr(module, found_class_name)

    raise ImportError("Could not find an object for %r" % (name,))


class Proxy:
    """
    Pass all function calls to instance, or to parent class if instance does not
    implement it.
    """

    def __init__(self, instance):
        self._instance = instance

    def __getattribute__(self, item):
        cls = object.__getattribute__(self, '_instance')

        if item == '_instance':
            return cls

        if hasattr(cls, item):
            return getattr(cls, item)

        return object.__getattribute__(self, item)


class LoadObjectProxy(Proxy):
    """
    Automatically load a class from any namespace, and pass all function calls to it,
    or to parent class if it is not implemented.
    """

    def __init__(self, name, *args, **kwargs):
        super().__init__(load_object(name)(*args, **kwargs))
