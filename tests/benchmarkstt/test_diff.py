from benchmarkstt import diff
import pytest

differs = [differ.cls for differ in diff.factory]
differs_decorator = pytest.mark.parametrize('differ', differs)


@differs_decorator
def test_one_insert(differ):
    sm = differ('b' * 100, 'a' + 'b' * 100)
    assert list(sm.get_opcodes()) == [('insert', 0, 0, 0, 1),
                                      ('equal', 0, 100, 1, 101)]
    sm = differ('b' * 100, 'b' * 50 + 'a' + 'b' * 50)
    assert list(sm.get_opcodes()) == [('equal', 0, 50, 0, 50),
                                      ('insert', 50, 50, 50, 51),
                                      ('equal', 50, 100, 51, 101)]
    ref = "a b c d e f"
    hyp = "a b d e kfmod fgdjn idf giudfg diuf dufg idgiudgd"
    sm = differ(ref, hyp)
    assert list(sm.get_opcodes()) == [('equal', 0, 3, 0, 3),
                                      ('delete', 3, 5, 3, 3),
                                      ('equal', 5, 10, 3, 8),
                                      ('insert', 10, 10, 8, 9),
                                      ('equal', 10, 11, 9, 10),
                                      ('insert', 11, 11, 10, 49)]


@differs_decorator
def test_one_delete(differ):
    sm = differ('a' * 40 + 'c' + 'b' * 40, 'a' * 40 + 'b' * 40)
    assert list(sm.get_opcodes()) == [('equal', 0, 40, 0, 40),
                                      ('delete', 40, 41, 40, 40),
                                      ('equal', 41, 81, 40, 80)]
