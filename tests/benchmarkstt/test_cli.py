import pytest
from benchmarkstt.cli import main, tools
from unittest import mock
from tempfile import TemporaryDirectory
import os
from io import StringIO
import shlex
from benchmarkstt.normalization import Base as NormalizationBase
from benchmarkstt.normalization import factory as normalization_factory
from benchmarkstt.diff.formatter import CLIDiffDialect
from benchmarkstt.__meta__ import __version__


cli_color_key = CLIDiffDialect().color_key

candide_lowercase = """
"there is a concatenation of events in this best of all possible worlds:
for if you had not been kicked out of a magnificent castle for love of
miss cunegonde: if you had not been put into the inquisition: if you had
not walked over america: if you had not stabbed the baron: if you had
not lost all your sheep from the fine country of el dorado: you would
not be here eating preserved citrons and pistachio-nuts."

"all that is very well," answered candide, "but let us cultivate our
garden."
"""


a_vs_b_result = '''wer
===

0.142857

worddiffs
=========

%s·TEST·my·data·should·be\033[31m·one\033[0m\033[32m·ONE\033[0m·difference

diffcounts
==========

equal: 6
replace: 1
insert: 0
delete: 0

''' % (cli_color_key,)


@pytest.mark.parametrize('argv,result', [
    [[], 2],
    ['invalidsubmodule', 2],
    ['normalization', 2],
    ['--help', 0],
    ['normalization -i ./resources/test/_data/candide.txt --lowercase', candide_lowercase],
    ['normalization -i ./resources/test/_data/candide.txt --lowercase --log', candide_lowercase],
    ['normalization -i ./resources/test/_data/candide.txt --file', 2],
    ['metrics -r ./resources/test/_data/a.txt -h ./resources/test/_data/b.txt', 2],
    ['metrics -r "HI" -h "HELLO" -rt argument -ht argument --wer', "wer\n===\n\n1.000000\n\n"],
    ['metrics --reference ./resources/test/_data/a.txt '
     '--hypothesis ./resources/test/_data/b.txt --wer --worddiffs --diffcounts', a_vs_b_result],
    ['metrics -r "HI" -h "HELLO" -rt argument -ht argument', 2],
    ['normalization -o /tmp/test.txt --lowercase', 2],
    ['metrics --reference "HELLO WORLD" --hypothesis "GOODBYE CRUEL WORLD" '
     '-rt argument -ht argument --worddiffs --output-format json',
     '[\n\t{"title": "worddiffs", "result": ['
     '{"type": "replace", "reference": "HELLO", "hypothesis": "GOODBYE"}, '
     '{"type": "insert", "reference": null, "hypothesis": "CRUEL"}, '
     '{"type": "equal", "reference": "WORLD", "hypothesis": "WORLD"}'
     ']}\n]\n'
     ],
    ['normalization -i ./resources/test/_data/candide.txt ./resources/test/_data/candide.txt -o /dev/null', 2],
    ['metrics -r "HELLO WORLD OF MINE" --hypothesis "GOODBYE CRUEL WORLD OF MINE" -rt argument -ht argument '
     '--worddiffs --output-format json',
     '[\n\t{"title": "worddiffs", "result": ['
     '{"type": "replace", "reference": "HELLO", "hypothesis": "GOODBYE"}, '
     '{"type": "insert", "reference": null, "hypothesis": "CRUEL"}, '
     '{"type": "equal", "reference": "WORLD", "hypothesis": "WORLD"}, '
     '{"type": "equal", "reference": "OF", "hypothesis": "OF"}, '
     '{"type": "equal", "reference": "MINE", "hypothesis": "MINE"}'
     ']}\n]\n'
     ],
    ['metrics -r "HELLO CRUEL WORLD OF MINE" -h "GOODBYE WORLD OF MINE" -rt argument -ht argument '
     '--worddiffs --output-format json',
     '[\n\t{"title": "worddiffs", "result": ['
     '{"type": "replace", "reference": "HELLO", "hypothesis": "GOODBYE"}, '
     '{"type": "delete", "reference": "CRUEL", "hypothesis": null}, '
     '{"type": "equal", "reference": "WORLD", "hypothesis": "WORLD"}, '
     '{"type": "equal", "reference": "OF", "hypothesis": "OF"}, '
     '{"type": "equal", "reference": "MINE", "hypothesis": "MINE"}'
     ']}\n]\n'
     ],
    ['metrics -r "HELLO CRUEL WORLD OF MINE" -h "GOODBYE WORLD OF MINE" -rt argument -ht argument '
     '--diffcounts --output-format json',
     '[\n\t{"title": "diffcounts", "result": {"equal": 3, "replace": 1, "insert": 0, "delete": 1}}\n]\n'
     ],
])
def test_clitools(argv, result, capsys):
    commandline_tester('benchmarkstt-tools', tools, argv, result, capsys)


@pytest.mark.parametrize('argv,result', [
    ['normalization -i ./resources/test/_data/candide.txt -o %s --lowercase', candide_lowercase],
])
def test_withtempfile(argv, result, capsys):
    with TemporaryDirectory() as tmpdir:
        tmpfile = os.path.join(tmpdir, 'tmpfile')
        argv = argv % ('"%s"' % (tmpfile,),)
        commandline_tester('benchmarkstt-tools', tools, argv, result, tmpfile)


@pytest.mark.parametrize('inputfile,argv,result', [
    ['./resources/test/_data/candide.txt', 'normalization --lowercase --log-level info', candide_lowercase],
])
def test_withstdin(inputfile, argv, result, capsys, monkeypatch):
    with open(inputfile) as f:
        try:
            monkeypatch.setattr('sys.stdin', StringIO(f.read()))
            commandline_tester('benchmarkstt-tools', tools, argv, result, capsys)
        finally:
            monkeypatch.delattr('sys.stdin')


@pytest.mark.parametrize('argv,result', [
    [[], 2],
    ['--version', 'benchmarkstt: %s\n' % (__version__,)],
    ['--help', 0],
    ['-r ./resources/test/_data/a.txt -h ./resources/test/_data/b.txt --wer --worddiffs --diffcounts', a_vs_b_result],
])
def test_cli(argv, result, capsys):
    commandline_tester('benchmarkstt', main, argv, result, capsys)


@pytest.mark.parametrize('argv', [
    '-r ./resources/test/_data/a.txt -h ./resources/test/_data/b.txt --replace --wer',
    '-r ./resources/test/_data/a.txt -h ./resources/test/_data/b.txt --replace "" "" "" --wer',
    '-r ./resources/test/_data/a.txt -h ./resources/test/_data/b.txt --replacewords "" "" "" --wer',
    '--log-level doesntexist',
])
def test_cli_errors(argv, capsys):
    commandline_tester('benchmarkstt', main, argv, 2, capsys)


@pytest.mark.parametrize('argv,result', [
    [
        '-r "And finally" -rt argument -h "and FINally" -ht argument --myownnormalizer --wer',
        'wer\n===\n\n0.000000\n\n'
    ],
])
def test_exensibility(argv, result, capsys):
    class MyOwnNormalizer(NormalizationBase):
        def _normalize(self, text: str) -> str:
            return text.upper()

    normalization_factory.register(MyOwnNormalizer)
    try:
        commandline_tester('benchmarkstt', main, argv, result, capsys)
    finally:
        del normalization_factory[MyOwnNormalizer]


@pytest.mark.parametrize('exc,argv', [
    [UnicodeDecodeError, '-r resources/test/_data/latin1.txt -h resources/test/_data/latin1.b.txt --wer'],
])
def test_cli_exceptions(exc, argv, capsys):
    with pytest.raises(exc):
        commandline_tester('benchmarkstt', main, argv, 2, capsys)


@pytest.mark.parametrize('encoding,argv,result', [
    ['latin1', '-r resources/test/_data/latin1.txt -h resources/test/_data/latin1.b.txt --wer -o markdown',
     '# wer\n\n0.375000\n\n'],
    ['iso-8859-1', '-r resources/test/_data/latin1.txt -h resources/test/_data/latin1.b.txt --wer -o markdown',
     '# wer\n\n0.375000\n\n'],
])
def test_encodings(encoding, argv, result, capsys, monkeypatch):
    try:
        monkeypatch.setenv('DEFAULT_ENCODING', encoding)
        commandline_tester('benchmarkstt', main, argv, result, capsys)
    finally:
        monkeypatch.delenv('DEFAULT_ENCODING')


@pytest.mark.parametrize('argv', [
    'normalization -i ./resources/test/_data/candide.txt --lower',
])
def test_clitools_errors(argv, capsys):
    commandline_tester('benchmarkstt-tools', tools, argv, 2, capsys)


def commandline_tester(prog_name, app, argv, result, capsys):
    if type(argv) is str:
        argv = shlex.split(argv)
    with mock.patch('sys.argv', [prog_name] + argv):
        if type(result) is int:
            with pytest.raises(SystemExit) as err:
                app()
            assert str(err).endswith(': %d' % (result,))
        else:
            with pytest.raises(SystemExit) as err:
                app()
            assert str(err).endswith(': 0')

            if type(capsys) is str:
                with open(capsys) as f:
                    assert f.read() == result
            else:
                captured = capsys.readouterr()
                if type(result) is list:
                    assert captured.out == result[0]
                    assert captured.err == result[1]
                else:
                    assert captured.out == result
