from benchmarkstt.normalization import core
from benchmarkstt.normalization import NormalizationComposite
from benchmarkstt.normalization import NormalizerConfig, available_normalizers
from benchmarkstt.normalization import factory


def test_name_to_normalizer():
    assert factory.get_class('Replace') is core.Replace
    assert factory.get_class('replace') is core.Replace


def test_available_normalizers():
    normalizers = available_normalizers()
    assert type(normalizers) is dict

    for name, conf in normalizers.items():
        # normalizer = factory.get_class(name)
        assert type(conf) is NormalizerConfig
        assert factory.is_valid(conf.cls)
        assert factory.get_class(name.upper()) is conf.cls


def test_is_normalizer():
    nope = [
        True,
        False,
        None,
        "replace",
        factory.is_valid,
        NormalizerConfig
    ]

    for not_normalizer in nope:
        assert factory.is_valid(not_normalizer) is False

    assert factory.is_valid(NormalizationComposite) is True
