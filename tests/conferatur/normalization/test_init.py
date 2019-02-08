from conferatur.normalization import *


def test_name_to_normalizer():
    assert name_to_normalizer('Replace') is core.Replace
    assert name_to_normalizer('replace') is core.Replace


def test_available_normalizers():
    normalizers = available_normalizers()
    assert type(normalizers) is dict

    for name, conf in normalizers.items():
        # normalizer = name_to_normalizer(name)
        assert type(conf) is NormalizerConfig
        assert is_normalizer(conf.cls)
        assert name_to_normalizer(name.upper()) is conf.cls


def test_is_normalizer():
    nope = [
        True,
        False,
        None,
        "replace",
        is_normalizer,
        NormalizerConfig
    ]

    for not_normalizer in nope:
        assert is_normalizer(not_normalizer) is False

    assert is_normalizer(core.Composite) is True