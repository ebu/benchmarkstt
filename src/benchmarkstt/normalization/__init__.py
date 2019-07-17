from benchmarkstt.normalization.logger import log
import logging
from benchmarkstt.factory import Factory
from benchmarkstt import settings
from benchmarkstt import csv
import os

_normalizer_namespaces = (
    "benchmarkstt.normalization.core",
    ""
)


logger = logging.getLogger(__name__)


class Base:
    @log
    def normalize(self, text: str) -> str:
        """
        Returns normalized text with rules supplied by the called class.
        """
        return self._normalize(text)

    def __repr__(self):
        return type(self).__name__

    def _normalize(self, text: str) -> str:
        raise NotImplementedError()


class BaseWithFileSupport(Base):
    """
    This kind of normalization class supports loading the values from a file, i.e.
    being wrapped in a core.File wrapper.
    """

    def _normalize(self, text: str) -> str:
        raise NotImplementedError()


class NormalizationComposite(Base):
    """
    Combining normalizers
    """

    def __init__(self, title=None):
        self._normalizers = []
        self._title = type(self).__name__ if title is None else title

    def add(self, normalizer):
        """Adds a normalizer to the composite "stack"
        """
        self._normalizers.append(normalizer)

    def _normalize(self, text: str) -> str:
        # allow for an empty file
        if not self._normalizers:
            return text

        for normalizer in self._normalizers:
            text = normalizer.normalize(text)
        return text

    def __repr__(self):
        return self._title


class File(Base):
    """
    Read one per line and pass it to the given normalizer

    :param str|class normalizer: Normalizer name (or class)
    :param str file: The file to read rules from
    :param str encoding: The file encoding

    :example text: "This is an Ex-Parakeet"
    :example normalizer: "regex"
    :example file: "./resources/test/normalizers/regex/en_US"
    :example encoding: "UTF-8"
    :example return: "This is an Ex Parrot"
    """

    def __init__(self, normalizer, file, encoding=None, path=None):
        if encoding is None:
            encoding = settings.default_encoding

        title = file
        if path is not None:
            file = os.path.join(path, file)

        with open(file, encoding=encoding) as f:
            self._normalizer = NormalizationComposite(title=title)

            for line in csv.reader(f):
                try:
                    self._normalizer.add(normalizer(*line))
                except TypeError as e:
                    raise ValueError("Line %d: %s" % (line.lineno, str(e)))

    def _normalize(self, text: str) -> str:
        return self._normalizer.normalize(text)


factory = Factory(Base, _normalizer_namespaces)


class FileFactory(Factory):
    def create(self, name, file=None, encoding=None, path=None):
        cls = super().__getitem__(name)
        return File(cls, file, encoding, path=path)

    def __getitem__(self, item):
        raise NotImplementedError("Not supported")


file_factory = FileFactory(BaseWithFileSupport, _normalizer_namespaces)
