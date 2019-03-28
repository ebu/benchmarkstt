from benchmarkstt.segmentation import core
from benchmarkstt.schema import Word
import pytest


@pytest.mark.parametrize('text,expected', [
    ('hello    world! how are you doing?!    ', ['hello    ', 'world! ', 'how ', 'are ', 'you ', 'doing?!    ']),
    ('\nhello    world! how are you doing?!    ', ['\nhello    ', 'world! ', 'how ', 'are ', 'you ', 'doing?!    ']),
    ('single-word', ['single-word']),
    (' test', [' test']),
    ('  test', ['  test']),
    ('  test  ', ['  test  ']),
    ('test  ', ['test  ']),
    ('test  B', ['test  ', 'B']),
    ('test  B ', ['test  ', 'B ']),
    ('\n\n', ['\n\n'])
])
def test_simple(text, expected):
    result = list(core.Simple(text))
    assert ''.join([word['@raw'] for word in result]) == text
    assert len(result) == len(expected)

    for i in range(0, len(expected)):
        expected_raw = expected[i]
        gotten = result[i]
        assert type(gotten) is Word
        assert expected_raw == gotten['@raw']
        assert expected_raw.strip() == gotten['text']
