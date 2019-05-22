from benchmarkstt.modules import Modules
from benchmarkstt.normalization import cli


def test_module():
    modules = Modules('cli')
    assert modules['normalization'] is cli
    assert modules.normalization is cli
    for k, v in modules:
        assert modules[k] is v
        assert getattr(modules, k) is v

    keys = modules.keys()
    assert type(keys) is list
    assert 'normalization' in keys
