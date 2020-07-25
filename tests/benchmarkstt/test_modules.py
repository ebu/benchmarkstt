from benchmarkstt.modules import Modules
from benchmarkstt.normalization import _cli


def test_module():
    modules = Modules('cli')
    assert modules['normalization'] is _cli
    assert modules.normalization is _cli
    for k, v in modules:
        assert modules[k] is v
        assert getattr(modules, k) is v

    keys = modules.keys()
    assert type(keys) is list
    assert 'normalization' in keys
