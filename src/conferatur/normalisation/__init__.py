from collections import namedtuple
import inspect
from importlib import import_module
import textwrap
from typing import Dict
import re

_normaliser_namespaces = (
    "conferatur.normalisation.core",
    ""
)

NormaliserConfig = namedtuple('NormaliserConfig', ['name', 'cls', 'docs', 'optional_args', 'required_args'])


def is_normaliser(cls):
    return inspect.isclass(cls) and hasattr(cls, 'normalise')


def available_normalisers() -> Dict[str, NormaliserConfig]:
    ignored_normalisers = ('composite',)
    normalisers = {}
    core = import_module('conferatur.normalisation.core')
    for cls in dir(core):
        name = cls.lower()
        cls = getattr(core, cls)
        if name in ignored_normalisers or not is_normaliser(cls):
            continue

        docs = cls.__doc__
        # docs = docs.split(':param', 1)[0]
        # remove rst blocks
        # docs = re.sub(r'^\s*\.\. [a-z-]+::\s+[a-z]+\s*$', '', docs, flags=re.MULTILINE)
        docs = textwrap.dedent(docs).strip()

        argspec = inspect.getfullargspec(cls.__init__)
        args = list(argspec.args)[1:]
        defaults = []
        if argspec.defaults:
            defaults = list(argspec.defaults)

        defaults_idx = len(args) - len(defaults)
        required_args = args[0:defaults_idx]
        optional_args = args[defaults_idx:]

        normalisers[name] = NormaliserConfig(name=name, cls=cls, docs=docs,
                                             optional_args=optional_args, required_args=required_args)

    return normalisers


def name_to_normaliser(name):
    """
    Loads the proper normaliser based on a name

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
    for lookup in _normaliser_namespaces:
        try:
            module = '.'.join(filter(len, lookup.split('.') + requested_module))
            if module == '':
                continue
            module = import_module(module)

            if hasattr(module, requested_class):
                cls = getattr(module, requested_class)
                if inspect.isclass(cls) and hasattr(cls, 'normalise'):
                    return cls

            # fallback, check case-insensitive matches
            realname = [class_name for class_name in dir(module)
                        if class_name.lower() == lname and
                        is_normaliser(getattr(module, class_name))]

            if len(realname) > 1:
                raise ImportError("Cannot determine which class to use for '$s': %s" %
                                  (lname, repr(realname)))
            elif len(realname):
                return getattr(module, realname[0])
        except ModuleNotFoundError:
            pass

    raise ImportError("Could not find normaliser '%s'" % (name,))

