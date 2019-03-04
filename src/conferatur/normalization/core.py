"""
Some basic/simple normalization classes


Each normalization class has a method called `normalize`:

.. code-block:: python

    def normalize(text: str) -> str:
        "\""Returns normalized text with rules supplied by the called class.
        "\""

"""

import re
from unidecode import unidecode
from io import StringIO
import os
import inspect
from langcodes import best_match, standardize_tag
from conferatur import csv, normalization
from conferatur.normalization.logger import log

default_encoding = 'UTF-8'


class LocalizedFile:
    """
    Reads and applies normalization rules from a locale-based file, it will automatically determine the "best fit" for a given locale, if one is available.

    :param str|class normalizer: Normalizer name (or class)
    :param str locale: Which locale to search for
    :param PathLike path: Location of available locale files
    :param str encoding: The file encoding

    :example text: "This is an Ex-Parakeet"
    :example normalizer: "regexreplace"
    :example path: "./resources/test/normalizers/regexreplace"
    :example locale: "en"
    :example encoding: "UTF-8"
    :example return: "This is an Ex Parrot"
    """

    def __init__(self, normalizer, locale: str, path: str, encoding=None):
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

        self._normalizer = File(normalizer, file, encoding=encoding)

    @log
    def normalize(self, text: str) -> str:
        return self._normalizer.normalize(text)


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

    @log
    def normalize(self, text: str) -> str:
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
    :example return: "She has the heart of formica"
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

    @log
    def normalize(self, text: str) -> str:
        return self._pattern.sub(self._replacement_callback, text)


class File:
    """
    Read one per line and pass it to the given normalizer

    :param str|class normalizer: Normalizer name (or class)
    :param str file: The file to read rules from
    :param str encoding: The file encoding

    :example text: "This is an Ex-Parakeet"
    :example normalizer: "regexreplace"
    :example file: "./resources/test/normalizers/regexreplace/en_US"
    :example encoding: "UTF-8"
    :example return: "This is an Ex Parrot"
    """

    def __init__(self, normalizer, file, encoding=None):
        try:
            cls = normalizer if inspect.isclass(normalizer) else normalization.name_to_normalizer(normalizer)
        except ValueError:
            raise ValueError("Unknown normalizer %s" %
                             (repr(normalizer)))

        if encoding is None:
            encoding = default_encoding

        with open(file, encoding=encoding) as f:
            self._normalizer = normalization.NormalizationComposite()

            for line in csv.reader(f):
                try:
                    self._normalizer.add(cls(*line))
                except TypeError as e:
                    raise ValueError("Line %d: %s" % (line.lineno, str(e)))

    @log
    def normalize(self, text: str) -> str:
        return self._normalizer.normalize(text)


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
    :example return: "HeHe! Hehehe!"
    """

    def __init__(self, search: str, replace: str=None):
        self._pattern = re.compile(search)
        self._substitution = replace if replace is not None else ''

    @log
    def normalize(self, text: str) -> str:
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
    :example return: "DasöderdieFlipperWåldGespütt"
    """

    def __init__(self):
        super().__init__(r'[^\w]+')


class Lowercase:
    """
    Lowercase the text


    :example text: "Easy, Mungo, easy... Mungo..."
    :example return: "easy, mungo, easy... mungo..."
    """

    @log
    def normalize(self, text: str) -> str:
        return text.lower()


class Unidecode:
    """
    Unidecode characters to ASCII form, see `Python's Unidecode package <https://pypi.org/project/Unidecode>`_ for more info.

    :example text: "𝖂𝖊𝖓𝖓 𝖎𝖘𝖙 𝖉𝖆𝖘 𝕹𝖚𝖓𝖘𝖙ü𝖈𝖐 𝖌𝖎𝖙 𝖚𝖓𝖉 𝕾𝖑𝖔𝖙𝖊𝖗𝖒𝖊𝖞𝖊𝖗?"
    :example return: "Wenn ist das Nunstuck git und Slotermeyer?"
    """

    @log
    def normalize(self, text: str) -> str:
        return unidecode(text)


class Config:
    r"""
    Use config notation to define normalization rules. This notation is a list of normalizers, one per line, with optional arguments (separated by a space).

    The normalizers can be any of the core normalizers, or you can refer to your own normalizer class (like you would use in a python import, eg. `my.own.package.MyNormalizerClass`).

    Additional rules:
      - Normalizer names are case-insensitive.
      - Arguments MAY be wrapped in double quotes.
      - If an argument contains a space, newline or double quote, it MUST be wrapped in double quotes.
      - A double quote itself is represented in this quoted argument as two double quotes: `""`.

    The normalization rules are applied top-to-bottom and follow this format:

    .. code-block:: text

        Normalizer1 arg1 "arg 2"
        # This is a comment
        
        Normalizer2
        # (Normalizer2 has no arguments)
        Normalizer3 "This is argument 1
        Spanning multiple lines
        " "argument 2"
        Normalizer4 "argument with double quote ("")"

    :param str config: configuration text

    :example text: "He bravely turned his tail and fled"
    :example config: '# using a simple config file\nLowercase \n\n    # it even supports comments\n# If there is a space in the argument, make sure you quote it though!\n  regexreplace "y t" "Y T"\n \n      # extraneous whitespaces are ignored \n     replace   e     a\n'
    :example return: "ha bravalY Turnad his tail and flad"
    """

    def __init__(self, config):
        self._parse_config(StringIO(config))

    def _parse_config(self, file):
        self._normalizer = normalization.NormalizationComposite()
        for line in csv.reader(file, dialect='whitespace'):
            try:
                normalizer = normalization.name_to_normalizer(line[0])
            except ValueError:
                raise ValueError("Unknown normalizer %s on line %d: %s" %
                                 (repr(line[0]), line.lineno, repr(' '.join(line))))
            self._normalizer.add(normalizer(*line[1:]))

    @log
    def normalize(self, text: str) -> str:
        return self._normalizer.normalize(text)


class ConfigFile(Config):
    """
    Load config from a file, see :py:class:`Config` for information about config notation

    :param typing.io.TextIO file: The file
    :param str encoding: The file encoding

    :example text: "He bravely turned his tail and fled"
    :example file: "./resources/test/normalizers/configfile.conf"
    :example encoding: "UTF-8"
    :example return: "ha bravalY Turnad his tail and flad"
    """

    def __init__(self, file, encoding=None):
        if encoding is None:
            encoding = default_encoding

        with open(file, encoding=encoding) as f:
            self._parse_config(f)

