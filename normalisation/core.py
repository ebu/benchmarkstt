"""
Some basic/simple normalisation classes
"""
import re
from unidecode import unidecode


class Replace:
    """
    Simple search replace

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
    >>> normaliser = RegexReplace('(scratch)', r"\1 (his arm's off)")
    >>> normaliser.normalise('Tis but a scratch.')
    "Tis but a scratch (his arm's off)."
    """
    def __init__(self, pattern: str, substitution: str=''):
        self._pattern = re.compile(pattern)
        self._substitution = substitution

    def normalise(self, text: str) -> str:
        return self._pattern.sub(self._substitution, text)


class AlphaNumeric(RegexReplace):
    """
    Simple alphanumeric filter

    >>> AlphaNumeric().normalise("She turned me into a newt.")
    'Sheturnedmeintoanewt'
    >>> AlphaNumeric().normalise("Das, öder die Flipper-Wåld Gespütt!")
    'DasderdieFlipperWldGesptt'
    """

    def __init__(self):
        super().__init__('[^A-Za-z0-9]+')


class AlphaNumericUnicode(RegexReplace):
    """
    >>> AlphaNumericUnicode().normalise("Das, öder die Flipper-Wåld Gespütt!")
    'DasöderdieFlipperWåldGespütt'
    """
    def __init__(self):
        super().__init__('[^\w]+')


class Lowercase:
    """
    >>> Lowercase().normalise('PRÁZdNÉ VLAŠToVKY')
    'prázdné vlaštovky'
    """

    def normalise(self, text: str):
        return text.lower()


class Unidecode:
    """
    >>> Unidecode().normalise('Eine große europäische Schwalbe')
    'Eine grosse europaische Schwalbe'
    """
    def normalise(self, text: str):
        return unidecode(text)


class Composite:
    """
    Combining normalisers

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

    def normalise(self, text: str):
        for normaliser in self._normalisers:
            text = normaliser.normalise(text)
        return text

