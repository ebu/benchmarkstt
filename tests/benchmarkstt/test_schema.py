from benchmarkstt.schema import Schema, Item, SchemaJSONError, SchemaInvalidItemError
import textwrap
from random import sample, randint
import pytest
from json.decoder import JSONDecodeError
import json
from collections import OrderedDict


def test_equality():
    assert Schema.loads('[]') == Schema()
    assert Schema([Item(item='test')]) != Schema()
    assert Item(item='test') == {'item': 'test'}
    assert Item({'item': 'test'}) == Item(item='test')


def test_encode():
    item = Item(item='word', start=12, end=23)
    itemdict = item._asdict()
    line = json.dumps(itemdict)
    line_formatted = json.dumps(itemdict, indent=2)

    assert item.json() == line
    assert item.json(indent=2) == line_formatted

    schema = Schema()
    schema.append(item)
    schema.append(item)
    assert len(schema) is 2
    assert schema.json() == '[%s, %s]' % ((line,) * 2)
    assert schema.json(indent=2) == '[\n%s,\n%s\n]' % ((textwrap.indent(line_formatted, '  '),) * 2)


def test_decode():
    res = Schema.loads('[{"item": "test"}]')

    assert type(res) is Schema
    assert len(res) is 1
    assert type(res[0]) is Item

    with pytest.raises(SchemaJSONError):
        Schema.loads('{"test": "test"}')

    with pytest.raises(JSONDecodeError):
        Schema.loads('InvalidJSON')

    with pytest.raises(SchemaJSONError):
        Schema.loads('"test"')

    with pytest.raises(SchemaJSONError):
        Schema.loads('24')

    with pytest.raises(SchemaInvalidItemError):
        Schema.loads('["test"]')


def random_str(minlen=None, maxlen=None):
    """
    Returns a random (printable) utf-8 string between approx. minlen and maxlen characters
    :return: str
    """
    if minlen is None:
        minlen = 10
    if maxlen is None:
        maxlen = 30
    return ''.join(chr(i) for i in sample(range(1, 0x10ffff), randint(minlen, maxlen)) if chr(i).isprintable())


def test_roundtrip():
    schema = Schema()
    testlen = 1
    for i in range(testlen):
        schema.append(OrderedDict(item=random_str(), start=randint(0, 1e10), end=randint(0, 1e10)))
        schema.append(Item(OrderedDict(item=random_str(), start=randint(0, 1e10), end=randint(0, 1e10))))

    schema.extend(list(schema))
    assert len(schema) == testlen * 4

    for item in schema:
        assert type(item) is Item

    json = schema.json()
    assert Schema.loads(json) == schema
    schema = Schema.loads(json)
    for item in schema:
        assert type(item) is Item
