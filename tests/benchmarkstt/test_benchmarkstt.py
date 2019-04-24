from benchmarkstt import DeferredRepr, DeferredStr, make_printable
import pytest


def cb(txt):
    def _():
        _.cb_count += 1
        return '[%s]' % (txt,)
    _.cb_count = 0
    return _


class ToDefer:
    def __init__(self, value):
        self.value = value
        self.cb_count = 0

    def __repr__(self):
        self.cb_count += 1
        return '<ToDefer:%s>' % (repr(self.value),)


def test_deferred_str():
    callback = cb('test')
    deferred = DeferredStr(callback)
    assert callback.cb_count == 0
    assert str(deferred) == '[test]'
    assert callback.cb_count == 1
    assert repr(deferred) == '[test]'
    assert callback.cb_count == 2


def test_deferred_repr():
    callback = ToDefer(None)
    deferred = DeferredRepr(callback)
    assert callback.cb_count == 0
    assert str(deferred) == '<ToDefer:None>'
    assert callback.cb_count == 1
    assert repr(deferred) == '<ToDefer:None>'
    assert callback.cb_count == 2


@pytest.mark.parametrize('orig,printable', [
    ['', ''],
    [' ', '·'],
    ['I\'m afraid I\thave no choice\nbut to sell you all for\tscientific experiments.',
     'I\'m·afraid·I␉have·no·choice␊but·to·sell·you·all·for␉scientific·experiments.']
])
def test_make_printable(orig, printable):
    assert make_printable(orig) == printable
