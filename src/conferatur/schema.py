"""
Defines the main schema for comparison and implements json serialization
"""
import json
from collections.abc import Mapping
from typing import Union
from collections import defaultdict
from collections import OrderedDict


class SchemaError(ValueError):
    """Top Error class for all schema related exceptions"""


class SchemaJSONError(SchemaError):
    """When loading incompatible JSON"""


class SchemaInvalidItemError(SchemaError):
    """Attempting to add an invalid item"""


class Word(Mapping):
    """
    Basic structure of each field to compare

    :raises: ValueError, SchemaInvalidItemError
    """

    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise ValueError('Expected max 1 argument')
        if len(args) and len(kwargs):
            raise ValueError("Cannot combine both a positional and keyword arguments")
        if len(args):
            if not isinstance(args[0], (dict, OrderedDict,)):
                raise SchemaInvalidItemError("Expected a dict object", args[0])
            self._val = OrderedDict(args[0])
        else:
            self._val = OrderedDict(kwargs)
        self.meta = Meta()

    def __getitem__(self, k):
        return self._val[k]

    def __len__(self) -> int:
        return len(self._val)

    def __iter__(self):
        return iter(self._val)

    def __repr__(self):
        return 'Word(%s)' % (self.json(),)

    def json(self, **kwargs):
        return Schema.dumps(self, **kwargs)

    def _asdict(self):
        return OrderedDict(self._val)

    def __eq__(self, other):
        return self._val == other

    def __ne__(self, other):
        return self._val != other


class Meta(defaultdict):
    """Containing metadata for an item, such as skipped"""


class Schema:
    """
    Basically a list of :py:class:`Word`s
    """

    def __init__(self, data=None):
        # make Schema.dump/dumps methods available as instance methods
        self.dump = self.__dump
        self.dumps = self.__dumps
        if data is None:
            self._data = []
        else:
            self._data = [item if type(item) is Word else Word(item) for item in data]

    def __repr__(self):
        return 'Schema(%s)' % (self.json(),)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, item):
        return self._data[item]

    """
    :raises: SchemaJSONError
    """
    @staticmethod
    def load(*args, **kwargs):
        return json.load(*args, **kwargs, cls=JSONDecoder)

    """
    :raises: SchemaJSONError
    """
    @staticmethod
    def loads(*args, **kwargs):
        return json.loads(*args, **kwargs, cls=JSONDecoder)

    @staticmethod
    def dump(cls, *args, **kwargs):
        return json.dump(cls, *args, **kwargs, cls=JSONEncoder)

    @staticmethod
    def dumps(cls, *args, **kwargs):
        return json.dumps(cls, *args, **kwargs, cls=JSONEncoder)

    def __dump(self, *args, **kwargs):
        return Schema.dump(self, *args, **kwargs)

    def __dumps(self, *args, **kwargs):
        return Schema.dumps(self, *args, **kwargs)

    def json(self, **kwargs):
        return self.dumps(**kwargs)

    def append(self, obj: Union[Word, dict]):
        if type(obj) is dict:
            obj = Word(obj)
        elif type(obj) is not Word:
            raise SchemaError("Wrong type", type(obj))
        self._data.append(obj)

    def extend(self, iterable):
        self._data.extend((item if type(item) is Word else Word(item) for item in iterable))

    def _aslist(self):
        return self._data

    def __eq__(self, other):
        return self._data == other

    def __ne__(self, other):
        return self._data != other


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoding for schema"""

    def default(self, obj):
        if isinstance(obj, Schema):
            return obj._aslist()
        if isinstance(obj, Word):
            return obj._asdict()
        return super().default(obj)


class JSONDecoder(json.JSONDecoder):
    """Custom JSON decoding for schema"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, object_hook=self.object_hook)

    def decode(self, *args, **kwargs):
        result = super().decode(*args, **kwargs)
        if type(result) is not list:
            raise SchemaJSONError("Expected a list")
        return Schema(result)

    @staticmethod
    def object_hook(obj):
        if type(obj) is not dict:
            raise SchemaJSONError("Expected an object")
        return Word(obj)

