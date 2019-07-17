"""
Some basic/simple normalization classes

"""

import re
import os
from unidecode import unidecode
from benchmarkstt import normalization
from benchmarkstt import config, settings
from contextlib import contextmanager
# from benchmarkstt.modules import LoadObjectProxy


file_types = (str,)
if hasattr(os, 'PathLike'):
    file_types = (str, os.PathLike)


class Replace(normalization.BaseWithFileSupport):
    """
    Simple search replace

    :param str search: Text to search for
    :param str replace: Text to replace with

    :example text: "Nudge nudge!"
    :example search: "nudge"
    :example replace: "wink"
    :example return: "Nudge wink!"
    """

    def __init__(self, search: str, replace: str):
        self._search = search
        self._replace = replace

    def _normalize(self, text: str) -> str:
        return text.replace(self._search, self._replace)


class ReplaceWords(normalization.BaseWithFileSupport):
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
        if len(self._replace) == 0:
            return ''

        if matches.group(0)[0].isupper():
            return ''.join([self._replace[0].upper(), self._replace[1:]])

        return ''.join([self._replace[0].lower(), self._replace[1:]])

    def _normalize(self, text: str) -> str:
        return self._pattern.sub(self._replacement_callback, text)


class Regex(normalization.BaseWithFileSupport):
    r"""
    Simple regex replace. By default the pattern is interpreted
    case-sensitive.

    Case-insensitivity is supported by adding inline modifiers.

    You might want to use capturing groups to preserve the case. When replacing
    a character not captured, the information about its case is lost...

    Eg. would replace "HAHA! Hahaha!" to "HeHe! Hehehe!":

     +------------------+-------------+
     | search           | replace     |
     +==================+=============+
     | :code:`(?i)(h)a` | :code:`\1e` |
     +------------------+-------------+


    No regex flags are set by default, you can set them yourself though in the
    regex, and combine them at will, eg. multiline, dotall and ignorecase.

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

    def __init__(self, search: str, replace: str):
        self._pattern = re.compile(search)
        self._substitution = replace

    def _normalize(self, text: str) -> str:
        return self._pattern.sub(self._substitution, text)


class Lowercase(normalization.Base):
    """
    Lowercase the text


    :example text: "Easy, Mungo, easy... Mungo..."
    :example return: "easy, mungo, easy... mungo..."
    """

    def _normalize(self, text: str) -> str:
        return text.lower()


class Unidecode(normalization.Base):
    """
    Unidecode characters to ASCII form, see `Python's Unidecode package
    <https://pypi.org/project/Unidecode>`_ for more info.

    :example text: "𝖂𝖊𝖓𝖓 𝖎𝖘𝖙 𝖉𝖆𝖘 𝕹𝖚𝖓𝖘𝖙ü𝖈𝖐 𝖌𝖎𝖙 𝖚𝖓𝖉 𝕾𝖑𝖔𝖙𝖊𝖗𝖒𝖊𝖞𝖊𝖗?"
    :example return: "Wenn ist das Nunstuck git und Slotermeyer?"
    """

    def _normalize(self, text: str) -> str:
        return unidecode(text)


class ConfigSectionNotFoundError(ValueError):
    """
    Raised when a requested config section was not found
    """


class Config(normalization.Base):
    doc_string = r"""
    Use config file notation to define normalization rules. This notation is a
    list of normalizers, one per line.

    Each normalizer that is based needs a file is followed by a file name of a
    csv, and can be optionally followed by the file encoding (if different than
    default).
    All options are loaded in from this csv and applied to the normalizer.

    The normalizers can be any of the core normalizers, or you can refer to your
    own normalizer class (like you would use in a python import, eg.
    `my.own.package.MyNormalizerClass`).

    Additional rules:
      - Normalizer names are case-insensitive.
      - Arguments MAY be wrapped in double quotes.
      - If an argument contains a space, newline or double quote, it MUST be
        wrapped in double quotes.
      - A double quote itself is represented in this quoted argument as two
        double quotes: `""`.

    The normalization rules are applied top-to-bottom and follow this format:

    .. code-block:: text

        {[section]}
        # This is a comment

        # (Normalizer2 has no arguments)
        lowercase

        # loads regex expressions from regexrules.csv in "utf 8" encoding
        regex regexrules.csv "utf 8"

        # load another config file, [section1] and [section2]
        config configfile.ini section1
        config configfile.ini section2

        # loads replace expressions from replaces.csv in default encoding
        replace     replaces.csv

    :param file: The config file
    :param encoding: The file encoding
    :param section: The subsection of the config file to use, {section}

    :example text: "He bravely turned his tail and fled"
    :example file: "./resources/test/normalizers/configfile.conf"
    :example encoding: "UTF-8"
    :example return: "ha bravalY Turnad his tail and flad"
    """

    MAIN_SECTION = object()
    _default_section = 'normalization'

    def __init__(self, file, section=None, encoding=None):
        if encoding is None or encoding == '':
            encoding = settings.default_encoding

        if section is None:
            section = self._default_section
        elif section is self.MAIN_SECTION:
            section = None

        if type(file) in file_types:
            # next filenames are relative from path of the config file...
            path = os.path.dirname(os.path.realpath(file))
            title = file

            with open(file, encoding=encoding) as f:
                reader = config.reader(f)
        else:
            path = None
            title = ''
            reader = config.reader(file)

        if section is not None:
            if section not in reader:
                raise ConfigSectionNotFoundError(section)

            reader = reader[section]
            title += '[%s]' % (section,)

        self._normalizer = normalization.NormalizationComposite(title)

        for line in reader:
            try:
                if line[0] in normalization.file_factory:
                    normalizer = normalization.file_factory.create(*line, path=path)
                else:
                    normalizer = normalization.factory.create(*line)
                self._normalizer.add(normalizer)
            except ImportError:
                raise ValueError("Unknown normalizer %s on line %d: %s" %
                                 (repr(line[0]), line.lineno, repr(' '.join(line))))

    def _normalize(self, text: str) -> str:
        return self._normalizer.normalize(text)

    @classmethod
    @contextmanager
    def default_section(cls, section):
        prev_section = cls._default_section
        cls._default_section = section
        try:
            cls.refresh_docstring()
            yield
        finally:
            cls._default_section = prev_section

    @classmethod
    def refresh_docstring(cls):
        section = 'defaults to %s' % (repr(cls._default_section),) if cls._default_section else 'no section by default'
        section_tag = '[%s]' % (cls._default_section,) if cls._default_section else ''
        cls.__doc__ = cls.doc_string.replace('{section}', section).replace('{[section]}', section_tag)


# For future versions
# class ExternalNormalizer(LoadObjectProxy, normalization.BaseWithFileSupport):
#     """
#     Automatically loads an external normalizer class.
#
#     :param name: The name of the normalizer to load (eg. mymodule.normalization.Normalizer)
#     """


Config.refresh_docstring()
