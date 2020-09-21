"""
Responsible for calculating metrics.

"""

from benchmarkstt.schema import Schema
from benchmarkstt.factory import Factory


class Metric:
    """
    Base class for metrics
    """
    def compare(self, ref: Schema, hyp: Schema):
        raise NotImplementedError()


factory = Factory(Metric)
