from conferatur.normalisation import *


def test_name_to_normaliser():
    assert name_to_normaliser('Replace') is core.Replace
    assert name_to_normaliser('replace') is core.Replace


def test_available_normalisers():
    normalisers = available_normalisers()
    assert type(normalisers) is dict

    for name, conf in normalisers.items():
        # normaliser = name_to_normaliser(name)
        assert type(conf) is NormaliserConfig
        assert is_normaliser(conf.cls)
        assert name_to_normaliser(name.upper()) is conf.cls


def test_is_normaliser():
    nope = [
        True,
        False,
        None,
        "replace",
        is_normaliser,
        NormaliserConfig
    ]

    for not_normaliser in nope:
        assert is_normaliser(not_normaliser) is False

    assert is_normaliser(core.Composite) is True