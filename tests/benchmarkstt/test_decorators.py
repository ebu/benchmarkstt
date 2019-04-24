import logging
from benchmarkstt.decorators import log_call


def test_log_call(caplog):
    logger = logging.getLogger()

    @log_call(logger, logging.WARNING)
    def test(*args, **kwargs):
        return 'result'

    test('arg1', arg2='someval')
    assert caplog.record_tuples == [
        ('root', logging.WARNING, "test('arg1', arg2='someval')")
    ]


def test_log_call2(caplog):
    logger = logging.getLogger('testname')
    caplog.set_level(logging.INFO)

    @log_call(logger, result=True, log_level=logging.INFO)
    def test(*args, **kwargs):
        return 'result'

    test(arg2='someval')
    assert caplog.record_tuples == [
        ('testname', logging.INFO, "test(arg2='someval')"),
        ('testname', logging.INFO, 'test returned: result')
    ]


def test_log_call3(caplog):
    logger = logging.getLogger('testname')
    caplog.set_level(logging.DEBUG)

    @log_call(logger)
    def funcname():
        return None

    funcname()
    assert caplog.record_tuples == [
        ('testname', logging.DEBUG, "funcname()"),
    ]
