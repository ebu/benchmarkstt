from benchmarkstt.factory import Factory
from pytest import raises

module_name = __name__


class Base:
    pass


class ValidClass(Base):
    pass


class InvalidClass:
    pass


def test_factory_exception():
    factory = Factory(Base)
    assert factory.get_class('validclass') == ValidClass
    with raises(ValueError) as exc:
        factory.register(InvalidClass)

    assert "Invalid class (must inherit from Base class)" in str(exc)


def test_factory():
    factory = Factory(Base, [])
    factory.register(ValidClass)
    assert factory.get_class('validclass') == ValidClass
    factory.register(ValidClass, 'alias')
    assert factory.get_class('alias') == ValidClass

    assert type(factory.create('alias')) == ValidClass

    with raises(ValueError) as exc:
        factory.register(ValidClass)

    assert "Conflict: alias 'validclass' is already registered" in str(exc)

    with raises(ValueError) as exc:
        factory.register_namespace(module_name)

    assert "Conflict: alias 'validclass' is already registered" in str(exc)


def test_nodoclog(caplog):
    factory = Factory(Base)

    for conf in factory:
        pass

    assert caplog.record_tuples == [
        ('benchmarkstt.factory', 30, "No docstring for normalizer 'ValidClass'")
    ]
