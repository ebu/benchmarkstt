import pytest
import sys
from textwrap import dedent
from benchmarkstt.cli import main, tools
from unittest import mock

from benchmarkstt.__meta__ import __version__


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


@pytest.mark.parametrize('argv,result', [
    [[], 2],
    ['invalidsubmodule', 2],
    ['normalization', 2],
    ['--help', 0],
    ['normalization -i ./resources/test/_data/candide.txt --lowercase', candide_lowercase],
    ['normalization -i ./resources/test/_data/candide.txt --file', 2],
    ['metrics ./resources/test/_data/a.txt -h ./resources/test/_data/b.txt', 2],
    ['metrics "HI" "HELLO" -rt argument -ht argument --wer', "wer\n===\n\n1.000000\n\n"],
    ['metrics ./resources/test/_data/a.txt ./resources/test/_data/b.txt --wer --worddiffs --diffcounts',
     dedent('''
     wer
     ===

     0.142857

     worddiffs
     =========

     ·TEST·my·data·should·be\033[31m·one\033[0m\033[32m·ONE\033[0m·difference

     diffcounts
     ==========

     OpcodeCounts(equal=6, replace=1, insert=0, delete=0)

     ''').lstrip()]
])
def test_clitools(argv, result, capsys):
    commandline_tester('benchmarkstt-tools', tools, argv, result, capsys)


@pytest.mark.parametrize('argv,result', [
    [[], 2],
    ['--version', 'benchmarkstt: %s\n' % (__version__,)],
    ['--help', 0],
])
def test_cli(argv, result, capsys):
    commandline_tester('benchmarkstt', main, argv, result, capsys)


def commandline_tester(prog_name, app, argv, result, capsys):
    if type(argv) is str:
        argv = argv.split()
    with mock.patch('sys.argv', [prog_name] + argv):
        if type(result) is int:
            with pytest.raises(SystemExit) as err:
                app()
            assert str(err).endswith(': %d' % (result,))
        else:
            with pytest.raises(SystemExit) as err:
                app()
            assert str(err).endswith(': 0')

            captured = capsys.readouterr()
            if type(result) is list:
                assert captured.out == result[0]
                assert captured.err == result[1]
            else:
                assert captured.out == result
