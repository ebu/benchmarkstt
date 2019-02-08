from collections import namedtuple
import inspect
from importlib import import_module
from typing import Dict
from conferatur.docblock import format_docs

_normalizer_namespaces = (
    "conferatur.normalization.core",
    ""
)

NormalizerConfig = namedtuple('NormalizerConfig', ['name', 'cls', 'docs', 'optional_args', 'required_args'])


def is_normalizer(cls):
    return inspect.isclass(cls) and hasattr(cls, 'normalize')


def available_normalizers() -> Dict[str, NormalizerConfig]:
    normalizers = {}
    core = import_module('conferatur.normalization.core')
    for cls in dir(core):
        name = cls.lower()
        cls = getattr(core, cls)
        if not is_normalizer(cls):
            continue

        docs = format_docs(cls.__doc__)
        # docs = docs.split(':param', 1)[0]
        # remove rst blocks
        # docs = re.sub(r'^\s*\.\. [a-z-]+::\s+[a-z]+\s*$', '', docs, flags=re.MULTILINE)

        argspec = inspect.getfullargspec(cls.__init__)
        args = list(argspec.args)[1:]
        defaults = []
        if argspec.defaults:
            defaults = list(argspec.defaults)

        defaults_idx = len(args) - len(defaults)
        required_args = args[0:defaults_idx]
        optional_args = args[defaults_idx:]

        normalizers[name] = NormalizerConfig(name=name, cls=cls, docs=docs,
                                             optional_args=optional_args, required_args=required_args)

    return normalizers


def name_to_normalizer(name):
    """
    Loads the proper normalizer based on a name

    :param name: str
    :return: class

    .. doctest::

    """
    requested = name.split('.')
    requested_module = []

    if len(requested) > 1:
        requested_module = requested[:-1]

    requested_class = requested[-1]
    lname = requested_class.lower()
    for lookup in _normalizer_namespaces:
        try:
            module = '.'.join(filter(len, lookup.split('.') + requested_module))
            if module == '':
                continue
            module = import_module(module)

            if hasattr(module, requested_class):
                cls = getattr(module, requested_class)
                if inspect.isclass(cls) and hasattr(cls, 'normalize'):
                    return cls

            # fallback, check case-insensitive matches
            realname = [class_name for class_name in dir(module)
                        if class_name.lower() == lname and
                        is_normalizer(getattr(module, class_name))]

            if len(realname) > 1:
                raise ImportError("Cannot determine which class to use for '$s': %s" %
                                  (lname, repr(realname)))
            elif len(realname):
                return getattr(module, realname[0])
        except ModuleNotFoundError:
            pass

    raise ImportError("Could not find normalizer '%s'" % (name,))


class NormalizationComposite:
    """
    Combining normalizers

    """

    def __init__(self):
        self._normalizers = []

    def add(self, normalizer):
        """Adds a normalizer to the composite "stack"
        """
        self._normalizers.append(normalizer)

    def normalize(self, text: str) -> str:
        # allow for an empty file
        if not self._normalizers:
            return text

        for normalizer in self._normalizers:
            text = normalizer.normalize(text)
        return text
