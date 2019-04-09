import inspect
from benchmarkstt import DeferredRepr
import logging
from importlib import import_module
from benchmarkstt.docblock import format_docs
from collections import namedtuple
from typing import Dict

logger = logging.getLogger(__name__)

ClassConfig = namedtuple('ClassConfig', ['name', 'cls', 'docs', 'optional_args', 'required_args'])


class Factory:
    def __init__(self, base_class, namespaces=None):
        self.base_class = base_class
        if namespaces is None:
            self.namespaces = [base_class.__module__]
        else:
            self.namespaces = namespaces

        self._registered_classes = {}

        for namespace in self.namespaces:
            self.register_namespace(namespace)

    def load(self, *args, **kwargs):
        raise NotImplementedError()

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
        namespaces = self.namespaces
        requested = name.split('.')
        requested_module = []

        if len(requested) > 1:
            requested_module = requested[:-1]

        requested_class = requested[-1]
        normalized_name = self.normalize_class_name(requested_class)
        for lookup in namespaces:
            try:
                module = '.'.join(filter(len, lookup.split('.') + requested_module))
                if module == '':
                    continue
                module = import_module(module)

                if hasattr(module, requested_class):
                    cls = getattr(module, requested_class)
                    if self.is_valid(cls):
                        return cls

                # fallback, check case-insensitive matches
                realname = [class_name for class_name in dir(module)
                            if self.normalize_class_name(class_name) == normalized_name and
                            self.is_valid(getattr(module, class_name))]

                if len(realname) > 1:
                    raise ImportError("Cannot determine which class to use for '$s': %s" %
                                      (normalized_name, repr(realname)))
                elif len(realname):
                    return getattr(module, realname[0])
            except ModuleNotFoundError:
                pass

        raise ImportError("Could not find class '%s'" % (name,))

    def is_valid(self, tocheck):
        if tocheck is self.base_class:
            return False
        if not inspect.isclass(tocheck):
            return False
        if issubclass(tocheck, self.base_class):
            return True
        logger.info('Not a valid class (must inherit from Base class): "%s"', DeferredRepr(tocheck))
        return False

    def register_namespace(self, namespace):
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
            if clsname in self._registered_classes:
                raise ValueError("Conflict: class '%s' is already registered" % (clsname,))
            self._registered_classes[clsname] = cls

    def register(self, cls, alias=None):
        """
        Register
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
        if alias in self._registered_classes:
            raise ValueError("Conflict: alias '%s' is already registered" % (alias,))
        self._registered_classes[alias] = cls

    def __iter__(self):
        """
        Get available classes with a proper ClassConfig

        :return: A dictionary of registered classes
        :rtype: Dict[str, ClassConfig]
        """

        for clsname, cls in self._registered_classes.items():
            if cls.__doc__ is None:
                docs = ''
                logger.warning("No docstring for normalizer '%s'", cls.__name__)
            else:
                docs = cls.__doc__
            docs = format_docs(docs)
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

            yield ClassConfig(name=clsname, cls=cls, docs=docs,
                              optional_args=optional_args,
                              required_args=required_args)
