from benchmarkstt.metrics.core import DiffCounts, WER, BEER
from benchmarkstt.metrics.core import OpcodeCounts
from benchmarkstt.input.core import PlainText
import pytest


@pytest.mark.parametrize('a,b,exp', [
    # ('equal', 'replace', 'insert', 'delete')
    ['Hello Test', 'Hello kind Test', (2, 0, 1, 0)],
    ['aaa aa bb', 'aaa bb', (2, 0, 0, 1)],
    ['aaa aa bb', 'aaa cc bb', (2, 1, 0, 0)],
    ['a b c d e f g h i', 'a b c c c d f g i', (7, 0, 2, 2)],
    ['', 'inserts 3 words', (0, 0, 3, 0)],
    ['deletes 3 words', '', (0, 0, 0, 3)],
    ['changes 1 word', 'changes one word', (2, 1, 0, 0)],
    ['0 1 2 3 4', '0 1 22 2 3 4', (5, 0, 1, 0)],
    ['0 1 2 3 4', '0 1 2 3 4', (5, 0, 0, 0)],
    ['a b c d e f', 'a b d e kfmod fgdjn idf giudfg diuf dufg idgiudgd', (4, 1, 6, 1)],
    ['HELLO CRUEL WORLD OF MINE', 'GOODBYE WORLD OF MINE', (3, 1, 0, 1)],
])
def test_diffcounts(a, b, exp):
    assert DiffCounts().compare(PlainText(a), PlainText(b)) == OpcodeCounts(*exp)


@pytest.mark.parametrize('a,b,exp', [
    # (wer_strict, wer_hunt, wer_levenshtein)
    ['aa bb cc dd', 'aa bb cc dd', (0, 0, 0)],
    ['aa bb cc dd', 'aa bb ee dd', (.25, .25, .25)],
    ['aa bb cc dd', 'aa aa bb cc dd dd', (.5, .25, .5)],
    ['aa bb cc dd', '', (1, 0.5, 1)],
    ['', 'aa bb cc', (1, 1, 1)],
    ['aa', 'bb aa cc', (2, 1, 2)],
    ['a b c d e f', 'a b d e kfmod fgdjn idf giudfg diuf dufg idgiudgd', (8 / 6, 3 / 4, 8 / 6)],
    ['a b c d e f g h i j', 'a b e d c f g h i j', (.4, .2, .2)],
])
def test_wer(a, b, exp):
    wer_strict, wer_hunt, wer_levenshtein = exp

    assert WER(mode=WER.MODE_STRICT).compare(PlainText(a), PlainText(b)) == wer_strict
    assert WER(mode=WER.MODE_HUNT).compare(PlainText(a), PlainText(b)) == wer_hunt
    assert WER(mode=WER.MODE_LEVENSHTEIN).compare(PlainText(a), PlainText(b)) == wer_levenshtein


@pytest.mark.parametrize('a,b,entities_list,weights, exp', [
    ['madam is here', 'adam is here', ['madam', 'here'], [100, 10], (0.455, 2)],
    ['madam is here', 'adam is here', ['madam', 'here'], [0.9, 0.1], (0.450, 2)],
    ['madam is here', 'adam is here', ['madam', 'here'], [10, 100], (0.045, 2)],
    ['theresa may is here', 'theresa may is there', ['theresa may', 'here'], [10, 100], (0.455, 2)],
    ['theresa may is here', 'theresa may is there', ['theresa may', 'here'], [100, 10], (0.045, 2)],
    ['aa bb cc dd', 'aa bb cc dd', ['aa', 'bb'], [100, 10], (0.0, 2)],
    ['aa bb cc dd', 'aa bb cc dd', ['aa', 'bb'], [10, 100], (0.0, 2)],
    ['aa bb cc dd', 'aa bb cc dd ee ff gg hh', ['aa', 'ee'], [10, 100], (0.0, 1)],
    ['aa bb cc dd', 'aa bb cc d ee ff gg hh', ['aa bb', 'cc dd'], [100, 10], (0.045, 2)],
    ['aa bb cc dd', 'aa bb cc d ee ff gg hh', ['aa bb', 'cc dd'], [10, 100], (0.455, 2)],
    ['', 'aa bb cc d ee ff gg hh', ['aa bb', 'cc dd'], [10, 100], (0.000, 0)],
])
def test_beer(a, b, entities_list, weights, exp):

    beer_test = BEER()
    beer_test.set_entities(entities_list)
    beer_test.set_weight(weights)
    out = beer_test.compare(PlainText(a), PlainText(b))
    entities_list.append('w_av_beer')

    assert tuple(out['w_av_beer'].values()) == exp
    assert set(out.keys()) == set(entities_list)
