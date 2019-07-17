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
    factory = Factory(Base, [test_factory_exception.__module__])
    assert factory['validclass'] == ValidClass
    with raises(ValueError) as exc:
        factory.register(InvalidClass)

    assert "Invalid class (must inherit from Base class)" in str(exc)


def test_factory():
    factory = Factory(Base, [])
    assert factory.is_valid(ValidClass) is True

    factory.register(ValidClass)
    assert factory['validclass'] == ValidClass
    factory['alias'] = ValidClass
    assert factory['alias'] == ValidClass

    assert type(factory.create('alias')) == ValidClass

    with raises(ValueError) as exc:
        factory.register(ValidClass)

    assert "Conflict: alias 'validclass' is already registered" in str(exc)

    with raises(ValueError) as exc:
        factory.register_namespace(module_name)

    assert "Conflict: alias 'validclass' is already registered" in str(exc)

    del factory[ValidClass]
    assert type(factory.create('alias')) == ValidClass

    with raises(ImportError) as exc:
        factory.create('validclass')

    assert "Could not find class" in str(exc)

    factory.unregister('alias')

    with raises(ImportError) as exc:
        factory.create('alias')

    assert "Could not find class" in str(exc)


def test_nodoclog(caplog):
    factory = Factory(Base, [test_nodoclog.__module__])

    for conf in factory:
        conf.docs
        pass

    assert caplog.record_tuples == [
        ('benchmarkstt.factory', 30, "No docstring for 'validclass'")
    ]
