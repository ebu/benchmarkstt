"""
Responsible for normalization of text.
"""

import os
from abc import ABC, abstractmethod
from benchmarkstt.normalization.logger import log
from benchmarkstt.factory import CoreFactory
from benchmarkstt import settings
from benchmarkstt import csv


class _NormalizerNoLogs(ABC):
    """
    Abstract base class for normalization, without providing logging.
    """

    @abstractmethod
    def normalize(self, text: str) -> str:
        """
        Returns normalized text with rules supplied by the called class.
        """

        raise NotImplementedError()

    def __repr__(self):
        return type(self).__name__


class Normalizer(_NormalizerNoLogs):
    """
    Abstract base class for normalization
    """

    @log
    def normalize(self, text: str) -> str:
        """
        Returns normalized text with rules supplied by the called class.
        """
        return self._normalize(text)

    @abstractmethod
    def _normalize(self, text: str) -> str:
        """
        :meta public:
        """
        raise NotImplementedError()


class NormalizerWithFileSupport(Normalizer):
    """
    This kind of normalization class supports loading the values from a file, i.e.
    being wrapped in a core.File wrapper.
    """

    @abstractmethod
    def _normalize(self, text: str) -> str:
        """
        :meta public:
        """
        raise NotImplementedError()


class NormalizationAggregate(Normalizer):
    """
    Combining normalizers
    """

    def __init__(self, title=None):
        """
        :meta public:
        """
        self._normalizers = []
        self._title = type(self).__name__ if title is None else title

    def add(self, normalizer):
        """Adds a normalizer to the composite "stack"
        """
        self._normalizers.append(normalizer)

    def _normalize(self, text: str) -> str:
        """
        :meta public:
        """
        # allow for an empty file
        if not self._normalizers:
            return text

        for normalizer in self._normalizers:
            text = normalizer.normalize(text)
        return text

    def __repr__(self):
        return self._title


class File(Normalizer):
    """
    Read one per line and pass it to the given normalizer

    :param str|class normalizer: Normalizer name (or class)
    :param file: The file to read rules from
    :param encoding: The file encoding

    :example text: "This is an Ex-Parakeet"
    :example normalizer: "regex"
    :example file: "./resources/test/normalizers/regex/en_US"
    :example encoding: "UTF-8"
    :example return: "This is an Ex Parrot"
    """

    def __init__(self, normalizer, file, encoding=None, path=None):
        """
        :meta public:
        """
        if encoding is None:
            encoding = settings.default_encoding

        title = file
        if path is not None:
            file = os.path.join(path, file)

        with open(file, encoding=encoding) as f:
            self._normalizer = NormalizationAggregate(title=title)
            for line in csv.reader(f):
                try:
                    self._normalizer.add(normalizer(*line))
                except TypeError as e:
                    raise ValueError("%s:%d %r(%r) %r" % (file, line.lineno, normalizer, line, e))

    def _normalize(self, text: str) -> str:
        return self._normalizer.normalize(text)


class FileFactory(CoreFactory):
    def create(self, name, file=None, encoding=None, path=None):
        cls = super().__getitem__(name)
        return File(cls, file, encoding, path=path)

    def __getitem__(self, item):
        """
        :meta public:
        """
        raise NotImplementedError("Not supported")


factory = CoreFactory(_NormalizerNoLogs)
file_factory = FileFactory(NormalizerWithFileSupport, False)
