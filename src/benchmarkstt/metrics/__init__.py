from benchmarkstt.schema import Schema
from benchmarkstt.factory import Factory


class Base:
    """
    Base class for metrics
    """
    def compare(self, ref: Schema, hyp: Schema):
        raise NotImplementedError()


factory = Factory(Base)
