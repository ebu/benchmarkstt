from benchmarkstt import diff
from benchmarkstt.diff.core import RatcliffObershelp, Levenshtein
import pytest

differs = [differ.cls for differ in diff.factory if differ.name != 'levenshtein']
differs_decorator = pytest.mark.parametrize('differ', differs)

all_differs = [differ.cls for differ in diff.factory]
all_differs_decorator = pytest.mark.parametrize('differ', all_differs)


def clean_opcode(opcode):
    kind, alo, ahi, blo, bhi = opcode
    if kind == 'delete':  # blo and bhi are irrelevant
        blo = bhi = None
    elif kind == 'insert':
        ahi = None
    return kind, alo, ahi, blo, bhi


def clean_opcodes(opcodes):
    return list(map(clean_opcode, opcodes))


def test_simple_levenshtein_ratcliff_similarity():
    a = list('012345')
    b = list('023x45')
    assert(clean_opcodes(Levenshtein(a, b).get_opcodes()) ==
           clean_opcodes(RatcliffObershelp(a, b).get_opcodes()))


@differs_decorator
def test_simple(differ):
    sm = differ(
        '0123456HIJkopq',
        '0123456HIJKlmnopq'
    )
    assert(clean_opcodes(sm.get_opcodes()) ==
           clean_opcodes([('equal', 0, 10, 0, 10),
                          ('replace', 10, 11, 10, 14),
                          ('equal', 11, 14, 14, 17)]))


@differs_decorator
def test_one_insert(differ):
    sm = differ('b' * 100, 'a' + 'b' * 100)
    assert(clean_opcodes(sm.get_opcodes()) ==
           clean_opcodes([('insert', 0, 0, 0, 1),
                          ('equal', 0, 100, 1, 101)]))

    sm = differ('b' * 100, 'b' * 50 + 'a' + 'b' * 50)
    assert(clean_opcodes(sm.get_opcodes()) ==
           clean_opcodes([('equal', 0, 50, 0, 50),
                          ('insert', 50, 50, 50, 51),
                          ('equal', 50, 100, 51, 101)]))


@differs_decorator
def test_one_delete(differ):
    sm = differ('a' * 40 + 'c' + 'b' * 40, 'a' * 40 + 'b' * 40)
    assert(clean_opcodes(sm.get_opcodes()) ==
           clean_opcodes([('equal', 0, 40, 0, 40),
                          ('delete', 40, 41, 40, 40),
                          ('equal', 41, 81, 40, 80)]))


def test_ratcliffobershelp():
    ref = "a b c d e f"
    hyp = "a b d e kfmod fgdjn idf giudfg diuf dufg idgiudgd"
    sm = RatcliffObershelp(ref, hyp)
    assert(clean_opcodes(sm.get_opcodes()) ==
           clean_opcodes([('equal', 0, 3, 0, 3),
                          ('delete', 3, 5, 3, 3),
                          ('equal', 5, 10, 3, 8),
                          ('insert', 10, 10, 8, 9),
                          ('equal', 10, 11, 9, 10),
                          ('insert', 11, 11, 10, 49)]))
