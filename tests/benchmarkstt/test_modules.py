from benchmarkstt.modules import Modules
from benchmarkstt.cli.entrypoints import normalization


def test_module():
    modules = Modules('cli')
    assert modules['normalization'] is normalization
    assert modules.normalization is normalization
    for k, v in modules:
        assert modules[k] is v
        assert getattr(modules, k) is v

    keys = modules.keys()
    assert type(keys) is list
    assert 'normalization' in keys
