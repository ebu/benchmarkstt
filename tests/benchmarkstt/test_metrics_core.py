from benchmarkstt.metrics.core import DiffCounts, WER
from benchmarkstt.metrics.core import OpcodeCounts
from benchmarkstt.input.core import PlainText
import pytest


@pytest.mark.parametrize('a,b,exp', [
    # ('equal', 'replace', 'insert', 'delete')
    ['Hello Test', 'Hello kind Test', (2, 0, 1, 0)],
    ['aaa aa bb', 'aaa bb', (2, 0, 0, 1)],
    ['aaa aa bb', 'aaa cc bb', (2, 1, 0, 0)],
])
def test_diffcounts(a, b, exp):
    assert DiffCounts().compare(PlainText(a), PlainText(b)) == OpcodeCounts(*exp)


@pytest.mark.parametrize('a,b,exp', [
    # (strict_wer, hunt_wer)
    ['aa bb cc dd', 'aa bb cc dd', (0, 0)],
    ['aa bb cc dd', 'aa bb ee dd', (.25, .25)],
    ['aa bb cc dd', 'aa aa bb cc dd dd', (.5, .25)],
    ['aa bb cc dd', '', (1, 0.5)],
    ['', 'aa bb cc', (1, 1)],
    ['aa', 'bb aa cc', (2, 1)]
])
def test_wer(a, b, exp):
    wer_strict, wer_hunt = exp

    assert WER(mode=WER.MODE_STRICT).compare(PlainText(a), PlainText(b)) == wer_strict
    assert WER(mode=WER.MODE_HUNT).compare(PlainText(a), PlainText(b)) == wer_hunt
