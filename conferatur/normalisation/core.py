"""
Some basic/simple normalisation classes


"""
import re
from unidecode import unidecode
import csv
from importlib import import_module


class Replace:
    """
    Simple search replace

    .. doctest::

        >>> from conferatur.normalisation.core import Replace
        >>> normaliser = Replace('scratch', 'flesh wound')
        >>> normaliser.normalise('Tis but a scratch.')
        'Tis but a flesh wound.'
    """

    def __init__(self, search: str, replace: str=''):
        self._search = search
        self._replace = replace

    def normalise(self, text: str) -> str:
        return text.replace(self._search, self._replace)


class RegexReplace:
    r"""
    Simple regex replace

    .. doctest::

        >>> from conferatur.normalisation.core import RegexReplace
        >>> normaliser = RegexReplace('(scratch)', r"\1 (his arm's off)")
        >>> normaliser.normalise('Tis but a scratch.')
        "Tis but a scratch (his arm's off)."

        By default the pattern is interpreted case-sensitive,

        >>> RegexReplace('ha', 'he').normalise('HA! Hahaha!')
        'HA! Hahehe!'

        Case-sensitivity is supported by adding inline modifiers.
        You might want to use capturing groups to preserve the case.
        When replacing a character not captured, the information about
        its case is lost...

        >>> RegexReplace('(?i)(h)a', r'\1e').normalise('HAHA! Hahaha!')
        'HeHe! Hehehe!'

        No regex flags are set by default, you can set them yourself though in the regex,
        and combine them at will, eg. multiline, dotall and ignorecase:

        >>> RegexReplace('(?msi)new.line', 'newline').normalise("New\nline")
        'newline'


    """
    def __init__(self, pattern: str, substitution: str=None):
        self._pattern = re.compile(pattern)
        self._substitution = substitution if substitution is not None else ''

    def normalise(self, text: str) -> str:
        return self._pattern.sub(self._substitution, text)


class AlphaNumeric(RegexReplace):
    """
    Simple alphanumeric filter

    .. doctest::

        >>> from conferatur.normalisation.core import AlphaNumeric
        >>> AlphaNumeric().normalise("She turned me into a newt.")
        'Sheturnedmeintoanewt'
        >>> AlphaNumeric().normalise("Das, öder die Flipper-Wåld Gespütt!")
        'DasderdieFlipperWldGesptt'
    """

    def __init__(self):
        super().__init__('[^A-Za-z0-9]+')


class AlphaNumericUnicode(RegexReplace):
    """

    .. doctest::

        >>> from conferatur.normalisation.core import AlphaNumericUnicode
        >>> AlphaNumericUnicode().normalise("Das, öder die Flipper-Wåld Gespütt!")
        'DasöderdieFlipperWåldGespütt'
    """
    def __init__(self):
        super().__init__('[^\w]+')


class Lowercase:
    """
    Lowercase the text

    .. doctest::

        >>> from conferatur.normalisation.core import Lowercase
        >>> Lowercase().normalise('PRÁZdNÉ VLAŠToVKY')
        'prázdné vlaštovky'
    """

    def normalise(self, text: str) -> str:
        return text.lower()


class Unidecode:
    """
    Unidecode characters to ASCII form, see `Python's Unidecode package <https://pypi.org/project/Unidecode>`_ for more info.

    .. _see: https://pypi.org/project/Unidecode/

    .. doctest::

        >>> from conferatur.normalisation.core import Unidecode
        >>> Unidecode().normalise('Eine große europäische Schwalbe')
        'Eine grosse europaische Schwalbe'
    """
    def normalise(self, text: str) -> str:
        return unidecode(text)


class Composite:
    """
    Combining normalisers

    .. doctest::

        >>> from conferatur.normalisation.core import *
        >>> text = 'Knights who say: NI!'
        >>> normaliser = Composite()
        >>> normaliser.add(Lowercase())
        >>> normaliser.add(Unidecode())
        >>> normaliser.normalise(text)
        'knights who say: ni!'
        >>> comp = Composite()
        >>> comp.add(normaliser)
        >>> comp.add(Replace(' ni', ' Ekke Ekke Ekke Ekke Ptang Zoo Boing'))
        >>> comp.normalise(text)
        'knights who say: Ekke Ekke Ekke Ekke Ptang Zoo Boing!'
        >>> comp.add(Lowercase())
        >>> comp.normalise(text)
        'knights who say: ekke ekke ekke ekke ptang zoo boing!'
        >>> normaliser.add(Replace(' ni', ' nope'))
        >>> comp.normalise(text)
        'knights who say: nope!'
        >>> comp.normalise('Ich fälle Bäume und hüpf und spring.')
        'ich falle baume und hupf und spring.'
    """
    def __init__(self):
        self._normalisers = []

    def add(self, normaliser):
        self._normalisers.append(normaliser)

    def normalise(self, text: str) -> str:
        for normaliser in self._normalisers:
            text = normaliser.normalise(text)
        return text


class ConfigFile:
    """
    Reads and applies normalistion rules from a file.

    .. doctest::

        >>> from conferatur.normalisation.core import ConfigFile
        >>> from os.path import realpath, join
        >>> file = join(realpath('../'), 'resources', 'test', 'normalisers', 'configfile.conf')
        >>> normaliser = ConfigFile(file)
        >>> normaliser.normalise('Ee ecky thump!')
        'aa ackY Thump!'

    """

    _lookups = (
        "conferatur.normalisation.core",
        "conferatur.normalisation",
        ""
    )

    def __init__(self, file):
        self._normaliser = Composite()
        with open(file) as csvfile:
            reader = csv.reader(csvfile, delimiter=' ')
            for line in reader:
                # allow for comments
                if line[0].startswith('#'):
                    continue
                normaliser = self._get_class(line[0])
                self._normaliser.add(normaliser(*line[1:]))

    @classmethod
    def _get_class(cls, name):
        requested = name.split('.')
        requested_module = []

        if len(requested) > 1:
            requested_module = requested[:-1]

        requested_class = requested[-1]
        for lookup in cls._lookups:
            module = import_module('.'.join(filter(len, lookup.split('.') + requested_module)))
            if hasattr(module, requested_class):
                return getattr(module, requested_class)

        raise ImportError("Could not find '%s'" % (name,))

    def normalise(self, text: str) -> str:
        return self._normaliser.normalise(text)
