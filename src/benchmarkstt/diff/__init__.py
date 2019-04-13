from benchmarkstt.factory import Factory


class Base:
    def __init__(self, a='', b=''):
        raise NotImplementedError()

    def get_opcodes(self):
        """
        Return list of 5-tuples describing how to turn `a` into `b`.

        Each tuple is of the form `(tag, i1, i2, j1, j2)`. The first tuple has
        `i1 == j1 == 0`, and remaining tuples have `i1` equals the `i2` from the
        tuple preceding it, and likewise for `j1` equals the previous `j2`.

        The tags are strings, with these meanings:

         - 'replace': `a[i1:i2]` should be replaced by `b[j1:j2]`
         - 'delete': `a[i1:i2]` should be deleted. Note that `j1==j2` in this case.
         - 'insert': `b[j1:j2]` should be inserted at `a[i1:i1]`. Note that `i1==i2` in this case.
         - 'equal': `a[i1:i2] == b[j1:j2]`
        """
        raise NotImplementedError()


factory = Factory(Base)
