from benchmarkstt.segmentation import core
from benchmarkstt.schema import Item
import pytest
import re


@pytest.mark.parametrize('text,expected', [
    ('hello    world! how are you doing?!    ',
     ['hello    ', 'world! ', 'how ', 'are ', 'you ', 'doing?!    ']),
    ('\nhello    world! how are you doing?!    ',
     ['\n', 'hello    ', 'world! ', 'how ', 'are ', 'you ', 'doing?!    ']),
    ('single-word', ['single-word']),
    (' test', [' ', 'test']),
    ('  test', ['  ', 'test']),
    ('  test  ', ['  ', 'test  ']),
    ('test  ', ['test  ']),
    ('test  B', ['test  ', 'B']),
    ('test  B ', ['test  ', 'B ']),
    ('\n\n', ['\n\n']),
    ('A test \n', ['A ', 'test \n']),
    ('  \r\n Testing, st\n\r\ruff, okaT? \r\n\r\r',
     ['  \r\n ', 'Testing, ', 'st\n\r\r', 'uff, ', 'okaT? \r\n\r\r'],),
    ('Candide, "but let us cultivate our\ngarden."\n',
     ['Candide, ', '"but ', 'let ', 'us ', 'cultivate ', 'our\n', 'garden."\n'])
])
def test_simple(text, expected):
    result = list(core.Simple(text))
    assert ''.join([word['@raw'] for word in result]) == text
    assert len(result) == len(expected)

    segmentation_re = re.compile(r'[\n\t\s]+')

    for i in range(0, len(expected)):
        expected_raw = expected[i]
        gotten = result[i]
        assert type(gotten) is Item
        assert expected_raw == gotten['@raw']
        assert expected_raw.strip() == gotten['item']

        # test @segmentatedOn is either None or matches a whitespace
        assert gotten['@segmentedOn'] is None or segmentation_re.fullmatch(gotten['@segmentedOn']) is not None
