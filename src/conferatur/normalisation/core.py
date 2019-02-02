"""
Some basic/simple normalisation classes


"""
import re
from unidecode import unidecode
import csv
from io import StringIO
import os
import inspect
from langcodes import best_match, standardize_tag
from . import name_to_normaliser


default_encoding = 'utf-8'

# todo: use custom own csv reader to fix bugs
# known bugs:
# "#test" is incorrectly seen as a comment
# for config: if ending with a space, it will add a '' as last argument, need to pre-trim line


def _csvreader(file, *args, **kwargs):
    """
    Provides a enumerated csv reader Iterable. Empty and comment lines are filtered out.

    :param file:
    :param args:
    :param kwargs:
    :return: Iterable
    """

    def _csvreader_filter(arg):
        idx, line = arg
        # filter empty lines
        if not line:
            return False
        # filter comments
        if line[0].startswith('#'):
            return False
        # detect empty line if it only contains tabs
        if len(line) == 1 and line[0].strip() == '':
            return False
        return True

    return filter(_csvreader_filter, enumerate(csv.reader(file, *args, **kwargs), start=1))


class LocalisedFile:
    """
    Reads and applies normalisation rules from a locale-based file, it will automagically
    determine the "best fit" for a given locale, if one is available.

    :param normaliser: str|class Normaliser name or class
    :param locale: Which locale to search for
    :param path: Location of available locale files
    :param encoding: str The file encoding
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

    def normalise(self, text: str) -> str:
        return self._normaliser.normalise(text)


class Replace:
    """
    Simple search replace
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
    """

    def __init__(self, search: str, replace: str):
        search = search.strip()
        replace = replace.strip()
        
        args = tuple(map(re.escape, [
            search[0].upper(),
            search[0].lower(),
            search[1:] if len(search) > 1 else ''
        ]))
        regex = '(?<!\w)[%s%s]%s(?!\w)' % args
        self._pattern = re.compile(regex)
        self._replace = replace

    def _replacement_callback(self, matches):
        if matches.group(0)[0].isupper():
            return ''.join([self._replace[0].upper(), self._replace[1:]])

        return ''.join([self._replace[0].lower(), self._replace[1:]])

    def normalise(self, text: str) -> str:
        return self._pattern.sub(self._replacement_callback, text)


class File:
    r"""
    Read one per line and pass it to the given normaliser
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

            for idx, line in _csvreader(f, delimiter=',', skipinitialspace=True):
                try:
                    self._normaliser.add(cls(*line))
                except TypeError as e:
                    raise ValueError("Line %d: %s" % (idx, str(e)))

    def normalise(self, text: str) -> str:
        return self._normaliser.normalise(text)


class RegexReplace:
    r"""
    Simple regex replace. By default the pattern is interpreted
    case-sensitive.

    Case-insensitivity is supported by adding inline modifiers.
    You might want to use capturing groups to preserve the case.
    When replacing a character not captured, the information about
    its case is lost...

    Eg.
        search: ``(?i)(h)a``
        replace: ``\1e``
        would replace "HAHA! Hahaha!" to "HeHe! Hehehe!"

    No regex flags are set by default, you can set them yourself though in the regex,
    and combine them at will, eg. multiline, dotall and ignorecase.

    Eg.
        search: ``(?msi)new.line``
        replace: ``newline``
        would replace "New\nline" to "newline"
    """

    def __init__(self, search: str, replace: str=None):
        self._pattern = re.compile(search)
        self._substitution = replace if replace is not None else ''

    def normalise(self, text: str) -> str:
        return self._pattern.sub(self._substitution, text)


class AlphaNumeric(RegexReplace):
    """
    Simple alphanumeric filter

    """

    def __init__(self):
        super().__init__('[^A-Za-z0-9]+')


class AlphaNumericUnicode(RegexReplace):
    """
    Simple alphanumeric filter, takes into account all unicode alphanumeric characters

    """
    def __init__(self):
        super().__init__('[^\w]+')


class Lowercase:
    """
    Lowercase the text

    """

    def normalise(self, text: str) -> str:
        return text.lower()


class Unidecode:
    """
    Unidecode characters to ASCII form, see `Python's Unidecode package <https://pypi.org/project/Unidecode>`_ for more info.

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
    Use config notation to define normalisation rules. This notation is a list of normalisers,
    one per line, with optional arguments (separated by a space).

    The normalisers can be any of the core normalisers, or you can refer to your own normaliser
    class (like you would use in a python import, eg. `my.own.package.MyNormaliserClass`). Normaliser
    names are case-insensitive.

    Arguments MAY be wrapped in double quotes.
    If an argument contains a space, newline or double quote, it MUST be wrapped in double quotes.
    A double quote itself is represented in this quoted argument as two double quotes: `""`.

    The normalisation rules are applied top-to-bottom and follow this format:

    .. code-block:: none

        Normaliser1 argument1 "argument 2" "this is argument3 containing a double quote ("")"
        # This is a comment
        Normaliser2
        # (Normaliser2 has no arguments)
        Normaliser3 "This is argument 1
        Spanning multiple lines
        " "and this would be argument 2 still applying to Normaliser3"

    """

    def __init__(self, config):
        self._normaliser = Composite()
        for idx, line in _csvreader(StringIO(config), delimiter=' ', skipinitialspace=True):
            try:
                normaliser = name_to_normaliser(line[0])
            except ValueError:
                raise ValueError("Unknown normaliser %s on line %d: %s" %
                                 (repr(line[0]), idx, repr(' '.join(line))))
            self._normaliser.add(normaliser(*line[1:]))

    def normalise(self, text: str) -> str:
        return self._normaliser.normalise(text)

