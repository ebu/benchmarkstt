"""
Some basic/simple normalisation classes


"""
import re
from unidecode import unidecode
import csv
from importlib import import_module
from io import StringIO
import os


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


class Config:
    r"""
    Use config notation to define normalisation rules. This notation is a list of normalisers,
    one per line, with optional arguments (separated by a space).

    The normalisers can be any of the core normalisers, or you can refer to your own normaliser
    class (like you would use in a python import, eg. `my.own.package.MyNormaliserClass`). Normaliser
    names are case-sensitive.

    Arguments MAY be wrapped in double quotes.
    If an argument contains a space, newline or double quote, it MUST be wrapped in double quotes.
    A double quote itself is represented in this quoted argument as two double quotes: `""`.

    The normalisation rules are applies top-to-bottom and follow this format:

    .. code-block:: none

        Normaliser1 argument1 "argument 2" "this is argument3 containing a double quote ("") and spaces"
        # This is a comment
        Normaliser2
        # (Normaliser2 has no arguments)
        Normaliser3 "This is argument 1
        Spanning multiple lines
        " "and this would be argument 2 still applying to Normaliser3"


    .. doctest::

        >>> from conferatur.normalisation.core import ConfigFile
        >>> config = '''
        ... # using a simple config file
        ... lowercase
        ... # Let's replace double quotes with single quotes (note wrapping in double quotes,
        ... # to allow the use of double quotes in an argument.
        ... RegexReplace "[""]" '
        ... # A space in the argument: wrap in double quotes as well
        ... Replace 'ni' "'ecky ecky ecky'"
        ... '''
        >>> normaliser = Config(config)
        >>> normaliser.normalise('No! Not the Knights Who Say "Ni"!')
        "no! not the knights who say 'ecky ecky ecky'!"
        >>> # Lets replace spaces with a newline (without using regex), demonstrating multiline arguments
        >>> # also note that the normaliser name is case-insensitive
        >>> config = '''
        ... replace " " "
        ... "
        ... '''
        >>> normaliser = Config(config)
        >>> normaliser.normalise("None shall pass.")
        'None\nshall\npass.'
        >>> Config('Replace     t      " T "').normalise("test")
        ' T es T '
        >>> # Loading a custom normaliser that wraps the text in square brackets
        >>> Config('resources.test.normalisers.Testnormaliser').normalise('test')
        '[test]'
    """

    _lookups = (
        "conferatur.normalisation.core",
        "conferatur.normalisation",
        ""
    )

    def __init__(self, config):
        self._apply_file_like_object(StringIO(config))

    def _apply_file_like_object(self, file_like_object):
        self._normaliser = Composite()
        reader = csv.reader(file_like_object, delimiter=' ', skipinitialspace=True)
        for idx, line in enumerate(reader):
            # allow empty lines
            if len(line) == 0:
                continue
            # allow for comments
            if line[0].startswith('#'):
                continue
            try:
                normaliser = self._get_class(line[0])
            except ValueError:
                raise ValueError("Unknown normaliser %s on line %d: %s" %
                                 (repr(line[0]), idx, repr(' '.join(line))))
            self._normaliser.add(normaliser(*line[1:]))

    @classmethod
    def _get_class(cls, name):
        requested = name.split('.')
        requested_module = []

        if len(requested) > 1:
            requested_module = requested[:-1]

        requested_class = requested[-1]
        lname = name.lower()
        for lookup in cls._lookups:
            try:
                module = '.'.join(filter(len, lookup.split('.') + requested_module))
                module = import_module(module)
                if hasattr(module, requested_class):
                    return getattr(module, requested_class)
                # fallback, check case-insensitive matches
                realname = [class_name for class_name in dir(module)
                            if class_name.lower() == lname and type(getattr(module, class_name)) is type]
                if len(realname) > 1:
                    raise ImportError("Cannot determine which class to use for '$s': %s" %
                                      (lname, repr(realname)))
                elif len(realname):
                    return getattr(module, realname[0])
            except ModuleNotFoundError:
                pass

        raise ImportError("Could not find '%s'" % (name,))

    def normalise(self, text: str) -> str:
        return self._normaliser.normalise(text)


class ConfigFile(Config):
    """
    Reads and applies normalisation rules from a file.

    See :func:`conferatur.normalisation.core.Config` for information about the config file format.

    .. doctest::

        >>> from conferatur.normalisation.core import ConfigFile
        >>> file = './resources/test/normalisers/configfile.conf'
        >>> normaliser = ConfigFile(file)
        >>> normaliser.normalise('Ee ecky thump!')
        'aa ackY Thump!'

    """

    def __init__(self, filename):
        filename = os.path.realpath(filename)
        with open(filename) as csvfile:
            self._apply_file_like_object(csvfile)

