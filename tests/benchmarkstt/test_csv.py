from benchmarkstt.csv import *
import pytest
from io import StringIO


def _reader(text, *args, **kwargs):
    return list(reader(StringIO(text), *args, **kwargs))


def test_csv():
    assert _reader('replace," ","\n"') == [['replace', ' ', '\n']]
    assert type(reader(StringIO(''))) is Reader
    assert type(Reader(StringIO(''), DefaultDialect)) is Reader

    assert _reader('""') == [['']]

    assert _reader('') == []

    expected = [['Some line', 'some other'], ['dsfgdsg'], ['stay', 'togther  '],
                ['fsdss']]
    assert _reader('''
    Some line, some other \t  \t
    dsfgdsg

     \n         \t  \r
     \n \r

    "stay","togther  "

    # commented out
    fsdss
    ''') == expected

    assert _reader('"","test"," quiot"""') == [['', 'test', ' quiot"']]

    assert _reader('       val1     ,\t   val2  \n') == [['val1', 'val2']]

    assert _reader('    ","') == [[',']]

    assert _reader('""') == [['']]
    assert _reader('''
     "A,B","""A,B""",
    ''') == [['A,B', '"A,B"', '']]
    assert _reader('"A,B","""A,B""",') == [['A,B', '"A,B"', '']]

    assert _reader('     A\tB, \t   B\tA\t   ,') == [['A\tB', 'B\tA', '']]

    assert _reader('"#nocomment",#here  \n') == [['#nocomment', '#here']]
    assert _reader('"#nocomment",#here  ') == [['#nocomment', '#here']]
    assert _reader('\t t ') == [['t']]
    assert _reader('t') == [['t']]
    assert _reader('replace," ","\n"') == [['replace', ' ', '\n']]


def test_conf():
    def _reader(text):
        return list(reader(StringIO(text), 'whitespace'))

    assert _reader('replace " " "\n"') == [['replace', ' ', '\n']]

    expected = [['Lowercase'],
                ['regexreplace', 'y t', 'Y T'],
                ['Replace', 'e', 'a']]
    gotten = _reader('''# using a simple config file
Lowercase \n

# it even supports comments
# If there is a space in the argument, make sure you quote it though!
regexreplace "y t" "Y T"

      # extraneous whitespaces are ignored
   Replace   e     a''')
    assert gotten == expected

    file = './resources/test/normalizers/configfile.conf'
    with open(file) as f:
        assert list(reader(f, 'whitespace')) == expected

    expected = [
        ['Normalizer1', 'arg1', 'arg 2'],
        ['Normalizer2'],
        ['Normalizer3', 'This is argument 1\nSpanning multiple lines\n',
         'argument 2'],
        ['Normalizer4', 'argument with double quote (")']
    ]

    assert _reader("""
Normalizer1 arg1 "arg 2"
# This is a comment

Normalizer2
# (Normalizer2 has no arguments)
Normalizer3 "This is argument 1
Spanning multiple lines
" "argument 2"
Normalizer4 "argument with double quote ("")"
""") == expected

    assert _reader("lower case ") == [['lower', 'case']]
    assert _reader("lower case \n") == [['lower', 'case']]
    assert _reader('test "stuff "\t') == [['test', 'stuff ']]
    assert _reader('test "stuff "\n') == [['test', 'stuff ']]
    assert _reader('test "stuff\n\t"\n\t  \t  YEs    \t   \n') == \
        [['test', 'stuff\n\t'], ['YEs']]
    assert _reader("\n\n\n\nline5")[0].lineno == 5


def test_exceptions():
    with pytest.raises(InvalidDialectError):
        Reader(StringIO(''), dialect=InvalidDialectError)

    with pytest.raises(UnknownDialectError):
        _reader('', dialect='notknown')

    with pytest.raises(UnallowedQuoteError) as exc:
        _reader('test "')

    assert "Quote not allowed here" in str(exc)

    with pytest.raises(CSVParserError):
        _reader('stray"quote')

    with pytest.raises(UnclosedQuoteError) as exc:
        _reader('  s  ,"')

    assert "Unexpected end" in str(exc)

    with pytest.raises(UnallowedQuoteError):
        _reader('  fsd","')


def test_own_dialect():
    class OwnDialect(Dialect):
        delimiter = ';'

    assert _reader("Tester \n  No Trim  ", dialect=OwnDialect) == [['Tester '], ['  No Trim  ']]
