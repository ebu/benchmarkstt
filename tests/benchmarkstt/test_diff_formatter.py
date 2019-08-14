import benchmarkstt.diff.formatter as formatter
import pytest
from collections import OrderedDict

a = 'ABCDEFGHJKLMN'
b = 'ABBCDEFHHIJKLM'

cli_color_key = formatter.CLIDiffDialect().color_key


@pytest.mark.parametrize('dialect,expected', [
    ['text', 'AB\u0359BCDEFG\u0338HH\u0359I\u0359JKLMN\u0338'],
    ['cli', cli_color_key + 'A\033[32mB\033[0mBCDEF\033[31mG\033[0mH\033[32mHI\033[0mJKLM\033[31mN\033[0m'],
    ['html', 'A<span class="insert">B</span>BCDEF<span class="delete">G</span>'
             'H<span class="insert">HI</span>JKLM<span class="delete">N</span>'],
    ['json', '['
             '{"type": "equal", "reference": "A", "hypothesis": "A"}, '
             '{"type": "insert", "reference": null, "hypothesis": "B"}, '
             '{"type": "equal", "reference": "BCDEF", "hypothesis": "BCDEF"}, '
             '{"type": "delete", "reference": "G", "hypothesis": null}, '
             '{"type": "equal", "reference": "H", "hypothesis": "H"}, '
             '{"type": "insert", "reference": null, "hypothesis": "HI"}, '
             '{"type": "equal", "reference": "JKLM", "hypothesis": "JKLM"}, '
             '{"type": "delete", "reference": "N", "hypothesis": null}'
             ']'],
    ['list', [
        OrderedDict([('type', 'equal'), ('reference', 'A'), ('hypothesis', 'A')]),
        OrderedDict([('type', 'insert'), ('reference', None), ('hypothesis', 'B')]),
        OrderedDict([('type', 'equal'), ('reference', 'BCDEF'), ('hypothesis', 'BCDEF')]),
        OrderedDict([('type', 'delete'), ('reference', 'G'), ('hypothesis', None)]),
        OrderedDict([('type', 'equal'), ('reference', 'H'), ('hypothesis', 'H')]),
        OrderedDict([('type', 'insert'), ('reference', None), ('hypothesis', 'HI')]),
        OrderedDict([('type', 'equal'), ('reference', 'JKLM'), ('hypothesis', 'JKLM')]),
        OrderedDict([('type', 'delete'), ('reference', 'N'), ('hypothesis', None)])
    ]
    ]
])
def test_format_diff(dialect, expected):
    gotten = formatter.format_diff(a, b, dialect=dialect)
    assert gotten == expected


def test_no_diff():
    assert formatter.format_diff(a, a, dialect='cli') == (cli_color_key + a)


def test_dialect_exceptions():
    with pytest.raises(ValueError) as exc:
        formatter.DiffFormatter(dialect='dialectdoesntexist')
    assert 'Unknown diff dialect' in str(exc)


def test_default_dialect():
    assert formatter.DiffFormatter().diff(a, b) == formatter.format_diff(a, b)
