"""
Responsible for calculating metrics.

Structure
.........

.. image:: ../_static/uml/benchmarkstt.metrics.svg
    :alt: Package Structure - Click for details
    :target: ../_static/uml/benchmarkstt.metrics.svg
"""

from benchmarkstt.schema import Schema
from benchmarkstt.factory import Factory


class Base:
    """
    Base class for metrics
    """
    def compare(self, ref: Schema, hyp: Schema):
        raise NotImplementedError()


factory = Factory(Base)
