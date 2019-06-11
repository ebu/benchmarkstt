import inspect
import logging
from importlib import import_module
from benchmarkstt.docblock import format_docs
from collections import namedtuple
from typing import Dict

logger = logging.getLogger(__name__)


class ClassConfig(namedtuple('ClassConfig', ['name', 'cls', 'docs', 'optional_args', 'required_args'])):
    @property
    def docs(self):
        if self.cls.__doc__ is None:
            docs = ''
            logger.warning("No docstring for '%s'", self.name)
        else:
            docs = self.cls.__doc__
        return format_docs(docs)


class Factory:
    """
    Factory class with auto-loading of namespaces according to a base class.
    """

    def __init__(self, base_class, namespaces=None):
        self.base_class = base_class
        if namespaces is None:
            self.namespaces = [base_class.__module__ + '.core']
        else:
            self.namespaces = namespaces

        self._registry = {}

        for namespace in self.namespaces:
            self.register_namespace(namespace)

    def __contains__(self, item):
        return self.normalize_class_name(item) in self._registry

    def create(self, alias, *args, **kwargs):
        return self.get_class(alias)(*args, **kwargs)

    @staticmethod
    def normalize_class_name(clsname):
        """
        Normalizes the class name for automatic lookup of a class, by default
        this means lowercasing the class name, but may be overrided by a child
        class.

        :param str clsname: The class name
        :return: The normalized class name
        :rtype: str
        """
        return clsname.lower()

    def get_class(self, name):
        """
        Loads the proper class based on a name

        :param str name: Case-insensitive name of the class
        :return: The class
        :rtype: class
        """
        name = self.normalize_class_name(name)
        if name not in self._registry:
            raise ImportError("Could not find class '%s', available: %s" % (name, ', '.join(self._registry.keys())))

        return self._registry[name]

    def is_valid(self, tocheck):
        """
        Checks that tocheck is a valid class extending base_class

        :param class tocheck: The class to check
        :rtype: bool
        """

        if tocheck is self.base_class:
            return False
        if not inspect.isclass(tocheck):
            return False
        if not issubclass(tocheck, self.base_class):
            return False

        return True

    def keys(self):
        return self._registry.keys()

    def register_namespace(self, namespace):
        """
        Registers all valid classes from a given namespace

        :param str|module namespace:
        """

        module = '.'.join(filter(len, namespace.split('.')))
        if module == '':
            module = globals()
        else:
            module = import_module(module)

        for clsname in dir(module):
            cls = getattr(module, clsname)
            if not self.is_valid(cls):
                continue
            clsname = self.normalize_class_name(clsname)
            if clsname in self._registry:
                raise ValueError("Conflict: alias '%s' is already registered" % (clsname,))
            self._registry[clsname] = cls

    def register(self, cls, alias=None):
        """
        Register an alias for a class

        :param self.base_class cls:
        :param str|None alias: The alias to use when trying to get the class back,
                               by default will use normalized class name.
        :return: None
        """
        if not self.is_valid(cls):
            raise ValueError('Invalid class (must inherit from Base class)"')

        if alias is None:
            alias = cls.__name__

        alias = self.normalize_class_name(alias)
        if alias in self._registry:
            raise ValueError("Conflict: alias '%s' is already registered" % (alias,))
        self._registry[alias] = cls

    def __iter__(self):
        """
        Get available classes with a proper ClassConfig

        :return: A dictionary of registered classes
        :rtype: Dict[str, ClassConfig]
        """

        for clsname, cls in self._registry.items():
            argspec = inspect.getfullargspec(cls.__init__)
            args = list(argspec.args)[1:]
            defaults = []
            if argspec.defaults:
                defaults = list(argspec.defaults)

            defaults_idx = len(args) - len(defaults)
            required_args = args[0:defaults_idx]
            optional_args = args[defaults_idx:]

            yield ClassConfig(name=clsname, cls=cls,
                              docs=None,
                              optional_args=optional_args,
                              required_args=required_args)
