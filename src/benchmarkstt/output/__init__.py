"""
Responsible for dealing with output formats

Structure
.........

.. image:: ../_static/uml/benchmarkstt.output.svg
    :alt: Package Structure - Click for details
    :target: ../_static/uml/benchmarkstt.output.svg
"""

from benchmarkstt.factory import Factory


class Base:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def result(self, title, result):
        raise NotImplementedError()


factory = Factory(Base)
