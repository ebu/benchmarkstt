from functools import partial, wraps


class DeferredCallback:
    """Simple helper class to defer the execution of formatting functions until it is needed"""

    def __init__(self, cb, *args, **kwargs):
        self._cb = wraps(cb)(partial(cb, *args, **kwargs))

    def __str__(self):
        return self._cb()

    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, repr(self._cb()))


class DeferredList:
    def __init__(self, cb):
        self._cb = cb
        self._list = None

    @property
    def list(self):
        if self._list is None:
            self._list = self._cb()
        return self._list

    def __getitem__(self, item):
        return self.list[item]
