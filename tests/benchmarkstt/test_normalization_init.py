from benchmarkstt.normalization import core
from benchmarkstt.normalization import NormalizationComposite
from benchmarkstt.normalization import factory
from benchmarkstt.factory import ClassConfig
from inspect import isgenerator
import pytest


def test_name_to_normalizer():
    assert factory['Replace'] is core.Replace
    assert factory['replace'] is core.Replace


def test_available_normalizers():
    normalizers = iter(factory)
    assert isgenerator(normalizers)

    for conf in normalizers:
        name = conf.name
        assert type(conf) is ClassConfig
        assert factory.is_valid(conf.cls)
        assert factory[name.upper()] is conf.cls


def test_not_available_normalizers():
    with pytest.raises(ImportError):
        factory['SomeRandomUnavailableNormalizer']


def test_is_normalizer():
    nope = [
        True,
        False,
        None,
        "replace",
        factory.is_valid,
        ClassConfig
    ]

    for not_normalizer in nope:
        assert factory.is_valid(not_normalizer) is False

    assert factory.is_valid(NormalizationComposite) is True
    assert NormalizationComposite().normalize('NON-normalized') == 'NON-normalized'
