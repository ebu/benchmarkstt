"""
Some basic/simple normalisation classes


"""
import re
from unidecode import unidecode


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

    .. doctest::
        >>> from conferatur.normalisation.core import Lowercase
        >>> Lowercase().normalise('PRÁZdNÉ VLAŠToVKY')
        'prázdné vlaštovky'
    """

    def normalise(self, text: str) -> str:
        return text.lower()


class Unidecode:
    """

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

