import inspect
from benchmarkstt import DeferredRepr
import logging
from importlib import import_module

logger = logging.getLogger(__name__)


class Factory:
    def __init__(self, base_class, namespaces=None):
        self.base_class = base_class
        if namespaces is None:
            self.namespaces = [base_class.__module__]
        else:
            self.namespaces = namespaces

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

    def list(self):
        pass
