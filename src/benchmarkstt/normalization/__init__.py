from collections import namedtuple
import inspect
from importlib import import_module
from typing import Dict
from benchmarkstt.docblock import format_docs
from benchmarkstt.normalization.logger import log
import logging
from benchmarkstt.core import Factory

_normalizer_namespaces = (
    "benchmarkstt.normalization.core",
    ""
)

NormalizerConfig = namedtuple('NormalizerConfig', ['name', 'cls', 'docs', 'optional_args', 'required_args'])

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


def is_normalizer(cls):
    return factory.is_valid(cls)


def available_normalizers() -> Dict[str, NormalizerConfig]:
    normalizers = {}
    core = import_module('benchmarkstt.normalization.core')
    for cls in dir(core):
        name = cls.lower()
        cls = getattr(core, cls)
        if not factory.is_valid(cls):
            continue

        if cls.__doc__ is None:
            docs = ''
            logger.warning("No docstring for normalizer '%s'", cls.__name__)
        else:
            docs = cls.__doc__
        docs = format_docs(docs)
        # docs = docs.split(':param', 1)[0]
        # remove rst blocks
        # docs = re.sub(r'^\s*\.\. [a-z-]+::\s+[a-z]+\s*$', '', docs, flags=re.MULTILINE)

        argspec = inspect.getfullargspec(cls.__init__)
        args = list(argspec.args)[1:]
        defaults = []
        if argspec.defaults:
            defaults = list(argspec.defaults)

        defaults_idx = len(args) - len(defaults)
        required_args = args[0:defaults_idx]
        optional_args = args[defaults_idx:]

        normalizers[name] = NormalizerConfig(name=name, cls=cls, docs=docs,
                                             optional_args=optional_args, required_args=required_args)

    return normalizers


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
