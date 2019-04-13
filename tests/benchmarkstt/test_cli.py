import pytest
import sys
from benchmarkstt.cli import main
from unittest import mock

from benchmarkstt.__meta__ import __version__


@pytest.mark.parametrize('argv,result', [
    [[], 2],
    [['--version'], 'benchmarkstt: %s\n' % (__version__,)],
    [['invalidsubmodule'], 2],
    [['normalization'], 2],
    [['--help'], 0],
])
def test_cli(argv, result, capsys):
    with mock.patch('sys.argv', ['benchmarkstt'] + argv):
        if type(result) is int:
            with pytest.raises(SystemExit) as err:
                main()
            assert str(err).endswith(': %d' % (result,))
        else:
            with pytest.raises(SystemExit) as err:
                main()
            assert str(err).endswith(': 0')

            captured = capsys.readouterr()
            if type(result) is list:
                assert captured.out == result[0]
                assert captured.err == result[1]
            else:
                assert captured.out == result
