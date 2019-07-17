import benchmarkstt.csv as csv
import pytest
from io import StringIO

example1 = '''
Some line, some other \t  \t
dsfgdsg

 \n         \t  \r
 \n \r

"stay","togther  "

# commented out
fsdss
'''

expected1 = [['Some line', 'some other'], ['dsfgdsg'], ['stay', 'togther  '], ['fsdss']]


def get_reader(text, *args, **kwargs):
    return list(csv.reader(StringIO(text), *args, **kwargs))


def test_csv():
    _reader = get_reader
    assert _reader('replace," ","\n"') == [['replace', ' ', '\n']]
    assert type(csv.reader(StringIO(''))) is csv.Reader
    assert type(csv.Reader(StringIO(''), csv.DefaultDialect)) is csv.Reader

    assert _reader('""') == [['']]

    assert _reader('') == []

    assert _reader(example1) == expected1

    assert _reader('"","test"," quiot"""') == [['', 'test', ' quiot"']]

    assert _reader('       val1     ,\t   val2  \n') == [['val1', 'val2']]

    assert _reader('    ","') == [[',']]

    assert _reader('""') == [['']]
    assert _reader('''
     "A,B","""A,B""",
    ''') == [['A,B', '"A,B"', '']]
    assert _reader('"A,B","""A,B""",') == [['A,B', '"A,B"', '']]

    assert _reader('     A\tB, \t   B\tA\t   ,') == [['A\tB', 'B\tA', '']]

    assert _reader('"#nocomment",#yescomment\n') == [['#nocomment', '']]
    assert _reader('"#nocomment",#here  ') == [['#nocomment', '']]
    assert _reader('"#nocomment",#') == [['#nocomment', '']]
    assert _reader('"#nocomment"# test') == [['#nocomment']]
    assert _reader('"#nocomment"    # commented') == [['#nocomment']]
    assert _reader('\t t ') == [['t']]
    assert _reader('t') == [['t']]
    assert _reader('replace," ","\n"') == [['replace', ' ', '\n']]
    assert _reader(',') == [['', '']]
    assert _reader('#yescomment,#here  \n') == []
    assert _reader(r'''# test
"(?s)<\?xml.*</head>",""   # inline comment
   # ignore
"<[^>]+>"," " # test
"[,.-\?]", ""    # more comments''') == [['(?s)<\\?xml.*</head>', ''], ['<[^>]+>', ' '], ['[,.-\\?]', '']]

    assert _reader('test,ok\n\n   \n\t\n\t\n.\n\n') == [['test', 'ok'], ['.']]

    assert _reader('"Some", "words"   # comment') == [['Some', 'words']]


def test_conf():
    def _reader(text):
        return list(csv.reader(StringIO(text), 'whitespace'))

    assert _reader('replace " " "\n"') == [['replace', ' ', '\n']]

    expected = [['Lowercase'],
                ['regex', 'y t', 'Y T'],
                ['Replace', 'e', 'a']]
    gotten = _reader('''# using a simple config file
Lowercase \n

# it even supports comments
# If there is a space in the argument, make sure you quote it though!
regex "y t" "Y T"

      # extraneous whitespaces are ignored
   Replace   e     a''')
    assert gotten == expected

    expected = [['Lowercase'],
                ['regex', 'regextestforconf.csv'],
                ['Replace', 'simplereplacetestforconf.csv']]
    file = './resources/test/normalizers/configfile.conf'
    with open(file) as f:
        assert list(csv.reader(f, 'whitespace')) == expected

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
    assert _reader('# Remove XML tags\n"<[^>]+>" " " \n\n# Remove punctuation\n"[,.-]" " "') == \
        [['<[^>]+>', ' '], ["[,.-]", " "]]


def test_exceptions():
    _reader = get_reader

    with pytest.raises(csv.InvalidDialectError):
        csv.Reader(StringIO(''), dialect=csv.InvalidDialectError)

    with pytest.raises(csv.UnknownDialectError):
        _reader('', dialect='notknown')

    with pytest.raises(csv.UnallowedQuoteError) as exc:
        _reader('test "')

    assert "Quote not allowed here" in str(exc)

    with pytest.raises(csv.CSVParserError):
        _reader('stray"quote')

    with pytest.raises(csv.UnclosedQuoteError) as exc:
        _reader('  s  ,"')

    assert "Unexpected end" in str(exc)

    with pytest.raises(csv.UnallowedQuoteError):
        _reader('  fsd","')

    with pytest.raises(csv.UnallowedQuoteError) as exc:
        _reader('""test,')
    assert "Single quote inside quoted field" in str(exc)


def test_own_dialect():
    class OwnDialect(csv.Dialect):
        delimiter = ';'

    assert get_reader("Tester \n  No Trim  ", dialect=OwnDialect) == [['Tester '], ['  No Trim  ']]


def test_debugger(capsys):
    gotten = get_reader(example1, debug=True)

    assert gotten == expected1
    with open('./resources/test/_data/csv.debugging.output.txt', encoding='UTF-8') as f:
        expected_debug = f.read()
    assert capsys.readouterr().out == expected_debug
