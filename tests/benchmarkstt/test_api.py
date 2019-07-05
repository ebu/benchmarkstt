import pytest
from benchmarkstt.normalization.api import callback as normalization_api
import benchmarkstt.normalization.core as normalizers
from benchmarkstt.metrics.api import callback as metrics_api
import benchmarkstt.metrics.core as metrics
from collections import OrderedDict


@pytest.mark.parametrize('args,expected', [
    [[normalizers.Replace, 'HELLO', False, 'E', 'A'], {'text': 'HALLO'}],
    [
        [normalizers.Replace, 'HELLO', True, 'E', 'A'],
        {'text': 'HALLO', 'logs':
            [OrderedDict(
                title=None,
                stack=['Replace'],
                diff='H<span class="delete">E</span><span class="insert">A</span>LLO',
              )]}
    ],
    [
        [normalizers.Replace, 'HELLO', True, 'A', 'A'],
        {'text': 'HELLO', 'logs': []}
    ]
])
def test_normalization(args, expected):
    assert normalization_api(*args) == expected


@pytest.mark.parametrize('args,expected', [
    [[metrics.WER, 'HELLO WORLD', 'GOODBYE WORLD'], 0.5],
])
def test_metrics(args, expected):
    assert metrics_api(*args) == expected


def test_error():
    with pytest.raises(AssertionError) as exc:
        normalization_api(normalizers.Config, 'sometext', False, './resources/test/normalizers/invalidconfig.conf')

    assert 'Unexpected end' in str(exc)

    with pytest.raises(TypeError) as exc:
        metrics_api(metrics.WER)
