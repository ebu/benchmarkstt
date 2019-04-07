from benchmarkstt.schema import Schema


class Base:
    """
    Base class for differs
    """
    def compare(self, ref: Schema, hyp: Schema):
        raise NotImplementedError
