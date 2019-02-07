"""
Some basic/simple normalisation classes

"""

import re
from unidecode import unidecode
from io import StringIO
import os
import inspect
from langcodes import best_match, standardize_tag
from conferatur.normalisation import name_to_normaliser
from conferatur import csv
import logging
# from conferatur.decorators import log_call


default_encoding = 'UTF-8'
logger = logging.getLogger(__name__)


class LocalisedFile:
    """
    Reads and applies normalisation rules from a locale-based file, it will automagically determine the "best fit" for a given locale, if one is available.

    :param str|class normaliser: Normaliser name (or class)
    :param str locale: Which locale to search for
    :param PathLike path: Location of available locale files
    :param str encoding: The file encoding

    :example text: "This is an Ex-Parakeet"
    :example normaliser: "regexreplace"
    :example path: "./resources/test/normalisers/regexreplace"
    :example locale: "en"
    :example encoding: "UTF-8"
    :example return: "This is an Ex Parrot"
    """

    def __init__(self, normaliser, locale: str, path: str, encoding=None):
        path = os.path.realpath(path)
        if not os.path.isdir(path):
            raise NotADirectoryError("Expected '%s' to be a directory" % (str(path),))

        files = {standardize_tag(file): file
                 for file in os.listdir(path)
                 if os.path.isfile(os.path.join(path, file))}

        locale = standardize_tag(locale)
        match = best_match(locale, files.keys())[0]
        if match == 'und':
            raise FileNotFoundError("Could not find a locale file for locale '%s' in '%s'" % (locale, str(path)))

        file = os.path.join(path, files[match])

        if encoding is None:
            encoding = default_encoding

        self._normaliser = File(normaliser, file, encoding=encoding)

    # @log_call(logger, result=True)
    def normalise(self, text: str) -> str:
        return self._normaliser.normalise(text)


class Replace:
    """
    Simple search replace

    :param str search: Text to search for
    :param str replace: Text to replace with

    :example text: "Nudge nudge!"
    :example search: "nudge"
    :example replace: "wink"
    :example return: "Nudge wink!"
    """

    def __init__(self, search: str, replace: str=''):
        self._search = search
        self._replace = replace

    def normalise(self, text: str) -> str:
        return text.replace(self._search, self._replace)


class ReplaceWords:
    """
    Simple search replace that only replaces "words", the first letter will be
    checked case insensitive as well with preservation of case..

    :param str search: Word to search for
    :param str replace: Replace with

    :example text: "She has a heart of formica"
    :example search: "a"
    :example replace: "the"
    :example result: "She has the heart of formica"
    """

    def __init__(self, search: str, replace: str):
        search = search.strip()
        replace = replace.strip()
        
        args = tuple(map(re.escape, [
            search[0].upper(),
            search[0].lower(),
            search[1:] if len(search) > 1 else ''
        ]))
        regex = r'(?<!\w)[%s%s]%s(?!\w)' % args
        self._pattern = re.compile(regex)
        self._replace = replace

    def _replacement_callback(self, matches):
        if matches.group(0)[0].isupper():
            return ''.join([self._replace[0].upper(), self._replace[1:]])

        return ''.join([self._replace[0].lower(), self._replace[1:]])

    def normalise(self, text: str) -> str:
        return self._pattern.sub(self._replacement_callback, text)


class File:
    """
    Read one per line and pass it to the given normaliser

    :param str|class normaliser: Normaliser name (or class)
    :param str file: The file to read rules from
    :param str encoding: The file encoding

    :example text: "This is an Ex-Parakeet"
    :example normaliser: "regexreplace"
    :example file: "./resources/test/normalisers/regexreplace/en_US"
    :example encoding: "UTF-8"
    :example return: "This is an Ex Parrot"
    """

    def __init__(self, normaliser, file, encoding=None):
        try:
            cls = normaliser if inspect.isclass(normaliser) else name_to_normaliser(normaliser)
        except ValueError:
            raise ValueError("Unknown normaliser %s" %
                             (repr(normaliser)))

        if encoding is None:
            encoding = default_encoding

        with open(file, encoding=encoding) as f:
            self._normaliser = Composite()

            for line in csv.reader(f):
                try:
                    self._normaliser.add(cls(*line))
                except TypeError as e:
                    raise ValueError("Line %d: %s" % (line.lineno, str(e)))

    def normalise(self, text: str) -> str:
        return self._normaliser.normalise(text)


class RegexReplace:
    r"""
    Simple regex replace. By default the pattern is interpreted
    case-sensitive.

    Case-insensitivity is supported by adding inline modifiers.

    You might want to use capturing groups to preserve the case. When replacing a character not captured, the information about its case is lost...

    Eg. would replace "HAHA! Hahaha!" to "HeHe! Hehehe!":

     +------------------+-------------+
     | search           | replace     |
     +==================+=============+
     | :code:`(?i)(h)a` | :code:`\1e` |
     +------------------+-------------+


    No regex flags are set by default, you can set them yourself though in the regex, and combine them at will, eg. multiline, dotall and ignorecase.

    Eg. would replace "New<CRLF>line" to "newline":

     +------------------------+------------------+
     | search                 | replace          |
     +========================+==================+
     | :code:`(?msi)new.line` | :code:`newline`  |
     +------------------------+------------------+

    :example text: "HAHA! Hahaha!"
    :example search: '(?i)(h)a'
    :example replace: r'\1e'
    :example result: "HeHe! Hehehe!"
    """

    def __init__(self, search: str, replace: str=None):
        self._pattern = re.compile(search)
        self._substitution = replace if replace is not None else ''

    def normalise(self, text: str) -> str:
        return self._pattern.sub(self._substitution, text)


class AlphaNumeric(RegexReplace):
    """
    Simple alphanumeric filter

    :example text: "He's a lumberjack, and he's okay!"
    :example return: "Hesalumberjackandhesokay"
    """

    def __init__(self):
        super().__init__('[^A-Za-z0-9]+')


class AlphaNumericUnicode(RegexReplace):
    """
    Simple alphanumeric filter, takes into account all unicode alphanumeric characters

    :example text: "Das, öder die Flipper-Wåld Gespütt!"
    :example result: "DasöderdieFlipperWåldGespütt"
    """

    def __init__(self):
        super().__init__(r'[^\w]+')


class Lowercase:
    """
    Lowercase the text


    :example text: "Easy, Mungo, easy... Mungo..."
    :example result: "easy, mungo, easy... mungo..."
    """

    def normalise(self, text: str) -> str:
        return text.lower()


class Unidecode:
    """
    Unidecode characters to ASCII form, see `Python's Unidecode package <https://pypi.org/project/Unidecode>`_ for more info.

    :example text: "𝖂𝖊𝖓𝖓 𝖎𝖘𝖙 𝖉𝖆𝖘 𝕹𝖚𝖓𝖘𝖙ü𝖈𝖐 𝖌𝖎𝖙 𝖚𝖓𝖉 𝕾𝖑𝖔𝖙𝖊𝖗𝖒𝖊𝖞𝖊𝖗?"
    :example return: "Wenn ist das Nunstuck git und Slotermeyer?"
    """

    def normalise(self, text: str) -> str:
        return unidecode(text)


class Composite:
    """
    Combining normalisers

    """

    def __init__(self):
        self._normalisers = []

    def add(self, normaliser):
        """Adds a normaliser to the composite "stack"
        """
        self._normalisers.append(normaliser)

    def normalise(self, text: str) -> str:
        # allow for an empty file
        if not self._normalisers:
            return text

        for normaliser in self._normalisers:
            text = normaliser.normalise(text)
        return text


class Config:
    r"""
    Use config notation to define normalisation rules. This notation is a list of normalisers, one per line, with optional arguments (separated by a space).

    The normalisers can be any of the core normalisers, or you can refer to your own normaliser class (like you would use in a python import, eg. `my.own.package.MyNormaliserClass`).

    Additional rules:
      - Normaliser names are case-insensitive.
      - Arguments MAY be wrapped in double quotes.
      - If an argument contains a space, newline or double quote, it MUST be wrapped in double quotes.
      - A double quote itself is represented in this quoted argument as two double quotes: `""`.

    The normalisation rules are applied top-to-bottom and follow this format:

    .. code-block:: bash

        Normaliser1 arg1 "arg 2"
        # This is a comment
        
        Normaliser2
        # (Normaliser2 has no arguments)
        Normaliser3 "This is argument 1
        Spanning multiple lines
        " "argument 2"
        Normaliser4 "argument with double quote ("")"

    :param str config: configuration text

    :example text: "He bravely turned his tail and fled"
    :example config: '# using a simple config file\nLowercase \n\n    # it even supports comments\n# If there is a space in the argument, make sure you quote it though!\n  regexreplace "y t" "Y T"\n \n      # extraneous whitespaces are ignored \n     replace   e     a\n'
    :example return: "ha bravalY Turnad his tail and flad"
    """

    def __init__(self, config):
        self._parse_config(StringIO(config))

    def _parse_config(self, file):
        self._normaliser = Composite()
        for line in csv.reader(file, dialect='whitespace'):
            try:
                normaliser = name_to_normaliser(line[0])
            except ValueError:
                raise ValueError("Unknown normaliser %s on line %d: %s" %
                                 (repr(line[0]), line.lineno, repr(' '.join(line))))
            self._normaliser.add(normaliser(*line[1:]))

    def normalise(self, text: str) -> str:
        return self._normaliser.normalise(text)


class ConfigFile(Config):
    """
    Load config from a file, see :py:class:`Config` for information about config notation

    :param typing.io.TextIO file: The file
    :param str encoding: The file encoding

    :example text: "He bravely turned his tail and fled"
    :example file: "./resources/test/normalisers/configfile.conf"
    :example encoding: "UTF-8"
    :example return: "ha bravalY Turnad his tail and flad"
    """

    def __init__(self, file, encoding=None):
        if encoding is None:
            encoding = default_encoding

        with open(file, encoding=encoding) as f:
            self._parse_config(f)

