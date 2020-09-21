"""
Responsible for dealing with output formats

"""
from abc import ABC, abstractmethod
from collections import OrderedDict
from benchmarkstt.factory import CoreFactory


class Output(ABC):
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

    @abstractmethod
    def result(self, title, result):
        """
        :meta public:
        """
        raise NotImplementedError()


class SimpleTextBase(Output):
    @staticmethod
    def print(result):
        if hasattr(result, '_asdict'):
            result = result._asdict()

        if type(result) is float:
            print("%.6f" % (result,))
        elif type(result) is dict or type(result) is OrderedDict:
            for k, v in result.items():
                print("%s: %r" % (k, v))
        else:
            print(result)

    @abstractmethod
    def result(self, title, result):
        """
        :meta public:
        """
        raise NotImplementedError()


factory = CoreFactory(Output)
