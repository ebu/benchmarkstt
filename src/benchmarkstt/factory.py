import inspect
import logging
from importlib import import_module
from benchmarkstt.docblock import format_docs
from collections import namedtuple
from typing import Dict
from benchmarkstt.registry import Registry
from benchmarkstt.modules import load_object

logger = logging.getLogger(__name__)


class ClassConfig(namedtuple('ClassConfigTuple', ['name', 'cls', 'docs', 'optional_args', 'required_args'])):
    @property
    def docs(self):
        if self.cls.__doc__ is None:
            docs = ''
            logger.warning("No docstring for '%s'", self.name)
        else:
            docs = self.cls.__doc__
        return format_docs(docs)


class Factory(Registry):
    """
    Factory class with auto-loading of namespaces according to a base class.
    """

    def __init__(self, base_class, namespaces=None, methods=None):
        super().__init__()
        self.base_class = base_class
        self.methods = methods
        self.namespaces = [base_class.__module__] if namespaces is None else namespaces

        for namespace in self.namespaces:
            self.register_namespace(namespace)

    def __contains__(self, item):
        return super().__contains__(self.normalize_class_name(item))

    def __getitem__(self, item):
        """
        Loads the proper class based on a name

        :param item: Case-insensitive name of the class
        :return: The class
        :rtype: class
        """
        name = self.normalize_class_name(item)

        if name not in self._registry:
            raise ImportError("Could not find class '%s', available: %s" % (name, ', '.join(self._registry.keys())))

        return super().__getitem__(name)

    def __delitem__(self, key):
        if type(key) is not str:
            key = self.normalize_class_name(key.__name__)
        super().__delitem__(key)

    def create(self, alias, *args, **kwargs):
        return self[alias](*args, **kwargs)

    @staticmethod
    def normalize_class_name(clsname):
        """
        Normalizes the class name for automatic lookup of a class, by default
        this means lowercasing the class name, but may be overrided by a child
        class.

        :param clsname: The class name
        :return: The normalized class name
        :rtype: str
        """
        return clsname.lower()

    def is_valid(self, tocheck):
        """
        Checks that tocheck is a valid class extending base_class

        :param tocheck: The class to check
        :rtype: bool
        """

        if tocheck is self.base_class:
            return False
        if not inspect.isclass(tocheck):
            return False
        if inspect.isabstract(tocheck):
            return False
        if issubclass(tocheck, self.base_class):
            return True

        # if it contains all required methods, accept as duck
        if self.methods:
            return all(map(callable, (getattr(tocheck, method, None)
                                      for method in self.methods)))

        return False

    def register_namespace(self, namespace):
        """
        Registers all valid classes from a given namespace

        :param str|module namespace:
        """

        if namespace is None:
            module = globals()
        else:
            optional = namespace[0] == '?'
            if optional:
                namespace = namespace[1:]

            module = '.'.join(filter(len, namespace.split('.')))
            try:
                module = import_module(module)
            except ImportError as e:
                if optional:
                    logger.info(
                        "Could not load optional namespace %s for %s: %s",
                        namespace,
                        self.base_class.__name__,
                        e)
                else:
                    raise e

        for clsname in dir(module):
            cls = getattr(module, clsname)
            if not self.is_valid(cls):
                continue
            self.register(cls, clsname)

    def register_classname(self, name, alias=None):
        if alias is None:
            alias = name
        self.register(load_object(name), alias)

    def register(self, cls, alias=None):
        """
        Register an alias for a class

        :param self.base_class cls:
        :param str|None alias: The alias to use when trying to get the class back,
                               by default will use normalized class name.
        :return: None
        """
        if not self.is_valid(cls):
            raise ValueError('Invalid class, not recognized as a %s' % (self.base_class.__name__,))

        if alias is None:
            alias = cls.__name__

        alias = self.normalize_class_name(alias)
        super().register(alias, cls)

    def __iter__(self):
        """
        Get available classes with a proper ClassConfig

        :return: A dictionary of registered classes
        :rtype: Dict[ClassConfig]
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

            yield ClassConfig(name=clsname,
                              cls=cls,
                              docs=None,
                              optional_args=optional_args,
                              required_args=required_args)


class CoreFactory:
    _extra_namespaces = []

    def __init__(self, base_class, allow_duck=None):
        if allow_duck is None:
            allow_duck = True

        self._base_class = base_class
        self._base_class_abstract_methods = self._abstract_methods(base_class) if allow_duck else None
        self._instance = None

    def _factory(self):
        # defers registration until first usage
        if self._instance is None:
            self._instance = Factory(
                self._base_class,
                [self._base_class.__module__ + '.core'] + self._extra_namespaces,
                self._base_class_abstract_methods
            )

        return self._instance

    def __iter__(self):
        return self._factory().__iter__()

    def __getitem__(self, item):
        return self._factory().__getitem__(item)

    def __delitem__(self, item):
        return self._factory().__delitem__(item)

    def __contains__(self, item):
        return self._factory().__contains__(item)

    def keys(self):
        return self._factory().keys()

    def create(self, *args, **kwargs):
        return self._factory().create(*args, **kwargs)

    def is_valid(self, *args, **kwargs):
        return self._factory().is_valid(*args, **kwargs)

    def register(self, *args, **kwargs):
        return self._factory().register(*args, **kwargs)

    @classmethod
    def add_supported_namespace(cls, namespace):
        cls._extra_namespaces.append(namespace)

    @staticmethod
    def _abstract_methods(base_class):
        return list(base_class.__abstractmethods__)
