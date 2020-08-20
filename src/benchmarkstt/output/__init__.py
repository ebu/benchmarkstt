"""
Responsible for dealing with output formats

.. Structure
.. .........

.. .. autoclasstree:: benchmarkstt.output.core benchmarkstt.output
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
