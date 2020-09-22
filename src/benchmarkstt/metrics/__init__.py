"""
Responsible for calculating metrics.

"""

from abc import ABC, abstractmethod
from benchmarkstt.schema import Schema
from benchmarkstt.factory import CoreFactory


class Metric(ABC):
    """
    Base class for metrics
    """
    @abstractmethod
    def compare(self, ref: Schema, hyp: Schema):
        raise NotImplementedError()


factory = CoreFactory(Metric)
