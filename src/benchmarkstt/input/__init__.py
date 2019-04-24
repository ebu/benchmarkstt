"""
Subpackage responsible for dealing with input formats and converting them to benchmarkstt native schema
"""

from benchmarkstt.factory import Factory


class Base:
    def __iter__(self):
        """
        Each input class should be accessible as iterator, each iteration should
        return a Item, so the input format is essentially usable and can be easily
        converted to a :py:class:`benchmarkstt.schema.Schema`
        """
        raise NotImplementedError()


factory = Factory(Base)
