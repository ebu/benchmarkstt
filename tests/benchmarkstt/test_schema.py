from benchmarkstt.schema import Schema, Item, JSONEncoder
from benchmarkstt.schema import SchemaError, SchemaJSONError, SchemaInvalidItemError
import textwrap
from random import sample, randint
import pytest
from json.decoder import JSONDecodeError
import json
from collections import OrderedDict
from pytest import raises
import io


def test_equality():
    assert Schema.loads('[]') == Schema()
    assert Schema([Item(item='test')]) != Schema()
    assert Item(item='test') == {'item': 'test'}
    assert Item({'item': 'test', 'item2': 55}) == Item(item='test', item2=55)
    assert Item({'item2': 55, 'item': 'test'}) == Item(item='test', item2=55)


def test_encode():
    item = Item(item='word', start=12, end=23)
    itemdict = item._asdict()
    line = json.dumps(itemdict)
    line_formatted = json.dumps(itemdict, indent=2)

    assert item.json() == line
    assert item.json(indent=2) == line_formatted

    buffer = io.StringIO()
    Schema.dump(Schema([item]), buffer)
    assert ('[%s]' % (item.json(),)) == buffer.getvalue()

    buffer = io.StringIO()
    Schema([item]).dump(buffer)
    assert ('[%s]' % (item.json(),)) == buffer.getvalue()

    schema = Schema()
    schema.append(item)
    schema.append(item)
    assert len(schema) is 2
    assert schema.json() == '[%s, %s]' % ((line,) * 2)
    assert schema.json(indent=2) == '[\n%s,\n%s\n]' % ((textwrap.indent(line_formatted, '  '),) * 2)
    assert repr(schema) == ('Schema(%s)' % (schema.json()))

    class T:
        ok = False

    with raises(TypeError) as exc:
        assert json.dumps(T(), cls=JSONEncoder)
    assert "is not JSON serializable" in str(exc)


def test_decode():
    res = Schema.loads('[{"item": "test"}]')

    assert type(res) is Schema
    assert len(res) is 1
    assert type(res[0]) is Item

    schema = Schema.load(io.StringIO(res.json()))
    assert len(schema) is 1
    assert type(schema[0]) is Item
    assert schema == res

    with pytest.raises(SchemaJSONError):
        Schema.loads('{"test": "test"}')

    with pytest.raises(JSONDecodeError):
        Schema.loads('InvalidJSON')

    with pytest.raises(SchemaJSONError) as exc:
        Schema.loads('"test"')
    assert "Expected a list" in str(exc)

    with pytest.raises(SchemaJSONError) as exc:
        Schema.loads('24')
    assert "Expected a list" in str(exc)

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
        schema.append(dict(item=random_str(), start=randint(0, 1e10), end=randint(0, 1e10)))
        schema.append(Item(OrderedDict(item=random_str(), start=randint(0, 1e10), end=randint(0, 1e10))))

    schema.extend(list(schema))
    assert len(schema) == testlen * 4

    for item in schema:
        assert type(item) is Item

    json_ = schema.json()
    assert Schema.loads(json_) == schema
    schema = Schema.loads(json_)
    for item in schema:
        assert type(item) is Item


def test_exceptions():
    with raises(ValueError) as exc:
        Item(None, None)
    assert 'Expected max 1 argument' in str(exc)

    with raises(ValueError) as exc:
        Item(None, somekeyword=None)
    assert "Cannot combine both a positional and keyword arguments" in str(exc)

    schema = Schema()
    with raises(SchemaError) as exc:
        schema.append(None)
    assert "Wrong type" in str(exc)


def test_item():
    item1 = Item()
    assert len(item1) == 0
    assert repr(item1) == 'Item({})'

    item = Item(a='a_', b='b_')
    assert len(item) == 2
    for k in item:
        assert k+'_' == item[k]
    assert repr(item) in ['Item({"a": "a_", "b": "b_"})',
                          'Item({"b": "b_", "a": "a_"})']

    assert item1 != item
