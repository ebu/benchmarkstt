from benchmarkstt.diff.formatter import format_diff
import pytest

a = 'ABCDEFGHJKLMN'
b = 'ABBCDEFHHIJKLM'


@pytest.mark.parametrize('dialect,expected', [
    ['text', 'AB\u0359BCDEFG\u0338HH\u0359I\u0359JKLMN\u0338'],
    ['cli', 'A\033[32mB\033[0mBCDEF\033[31mG\033[0mH\033[32mHI\033[0mJKLM\033[31mN\033[0m'],
    ['html', 'A<span class="insert">B</span>BCDEF<span class="delete">G</span>'
             'H<span class="insert">HI</span>JKLM<span class="delete">N</span>']
])
def test_format_diff(dialect, expected):
    gotten = format_diff(a, b, dialect=dialect)
    assert gotten == expected
    assert gotten == expected


def test_format_replace():
    pass
    # assert format_diff('ABCDEF', 'ABBDEF', dialect='cli') == ''
