from benchmarkstt import diff
import pytest

differs = [differ.cls for differ in diff.factory]
differs_decorator = pytest.mark.parametrize('differ', differs)

# from benchmarkstt.segmentation import Base
# class CharSegmenter(Base):
#     def __init__(self, text: str):
#         self.text = text
#
#     def __iter__(self):
#         return iter(self.text)


# some tests copied from https://github.com/python/cpython/blob/master/Lib/test/test_difflib.py
# additional tests to follow


@differs_decorator
def test_one_insert(differ):
    sm = differ('b' * 100, 'a' + 'b' * 100)
    assert list(sm.get_opcodes()) == [('insert', 0, 0, 0, 1),
                                      ('equal', 0, 100, 1, 101)]
    sm = differ('b' * 100, 'b' * 50 + 'a' + 'b' * 50)
    assert list(sm.get_opcodes()) == [('equal', 0, 50, 0, 50),
                                      ('insert', 50, 50, 50, 51),
                                      ('equal', 50, 100, 51, 101)]


@differs_decorator
def test_one_delete(differ):
    sm = differ('a' * 40 + 'c' + 'b' * 40, 'a' * 40 + 'b' * 40)
    assert list(sm.get_opcodes()) == [('equal', 0, 40, 0, 40),
                                      ('delete', 40, 41, 40, 40),
                                      ('equal', 41, 81, 40, 80)]
