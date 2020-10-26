import pytest
from benchmarkstt.modules import Modules, load_object
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


def test_unknown_module():
    modules = Modules('cli')
    assert 'doesntexist' not in modules

    with pytest.raises(IndexError) as exc:
        modules['doesntexist']

    assert 'Module not found' in str(exc)


def test_hidden_module():
    modules = Modules('cli')

    with pytest.raises(IndexError) as exc:
        modules['benchmark']

    assert 'Module is hidden' in str(exc)
    assert 'benchmark' not in [m for m in modules]


def test_load_object():
    assert hasattr(
        load_object('benchmarkstt.normalization.core.Lowercase', False),
        'normalize'
    )

    assert hasattr(
        load_object('benchmarkstt.normalization.core.LOWERCASE'),
        'normalize'
    )

    with pytest.raises(ImportError) as exc:
        load_object('somemodule')

    assert 'Could not find an object' in str(exc)

    with pytest.raises(ImportError) as exc:
        load_object('benchmarkstt.doesntexist')

    assert 'Could not find an object' in str(exc)
