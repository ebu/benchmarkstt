from benchmarkstt.normalization.logger import log
import logging
from benchmarkstt.factory import Factory

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

    def _normalize(self, text: str) -> str:
        raise NotImplementedError()


factory = Factory(Base, _normalizer_namespaces)


class NormalizationComposite(Base):
    """
    Combining normalizers
    """

    def __init__(self):
        self._normalizers = []

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
