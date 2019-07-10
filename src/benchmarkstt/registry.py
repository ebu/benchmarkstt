class Registry:
    """
    Simple registry class holding aliases and their corresponding values
    """

    def __init__(self):
        self._registry = {}

    def __contains__(self, item):
        return item in self._registry

    def __getitem__(self, item):
        return self._registry[item]

    def __setitem__(self, key, value):
        if key in self._registry:
            raise ValueError("Conflict: alias '%s' is already registered" % (key,))
        self._registry[key] = value

    def __delitem__(self, key):
        del self._registry[key]

    def register(self, key, value):
        return self.__setitem__(key, value)

    def unregister(self, key):
        return self.__delitem__(key)

    def keys(self):
        return self._registry.keys()
