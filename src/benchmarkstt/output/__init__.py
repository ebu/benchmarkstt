"""
Responsible for dealing with output formats

"""

from benchmarkstt.factory import Factory


class Output:
    def __enter__(self):
        """
        :meta public:
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        :meta public:
        """
        pass

    def result(self, title, result):
        """
        :meta public:
        """
        raise NotImplementedError()


factory = Factory(Output)
