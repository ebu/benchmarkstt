"""
Normalisation based on locale

"""

from abc import ABC, abstractmethod
from . import core
import os
from langcodes import best_match, standardize_tag
import csv


class AbstractLocale(ABC):
    """
    Abstract Base Class for locale based normalisation, it will automagically determine
    which file is to be used.

    :param locale: Which locale to search for
    :param path: Location of available locale files
    """

    def __init__(self, locale: str, path: str):
        self._file = self.choose_file(locale, path)

    @staticmethod
    def choose_file(locale: str, path: str) -> str:
        """
        Method tasked with automagically determining the "best fit" for a given locale, if one is available

        :param locale: Which locale to search for
        :param path: Location of available locale files
        :return: Full path to file location
        """
        if not os.path.isdir(path):
            raise NotADirectoryError("Expected '%s' to be a directory" % (str(path),))

        files = {standardize_tag(file): file
                 for file in os.listdir(path)
                 if os.path.isfile(os.path.join(path, file))}

        locale = standardize_tag(locale)
        match = best_match(locale, files.keys())[0]
        if match == 'und':
            raise FileNotFoundError("Could not find a locale file for locale '%s' in '%s'" % (locale, str(path)))
        return os.path.join(path, files[match])

    def normalise(self, text: str) -> str:
        return self._normaliser.normalise(text)

    @property
    @abstractmethod
    def _normaliser(self):
        pass


class RegexReplace(AbstractLocale):
    """

    .. doctest::

        >>> from conferatur.normalisation.localized import RegexReplace
        >>> from os.path import dirname, realpath, join
        >>> path = realpath('../')
        >>> path = join(path, 'resources', 'test', 'normalisers', 'regexreplace')
        >>>
        >>> normaliser = RegexReplace('en_UK', path)
        >>> normaliser.normalise("You're like a German Par-a-keet")
        "You're like a German Parrot"
        >>> normaliser = RegexReplace('it', path)
        >>> normaliser.normalise("grande caldo, grande problema, grande ala, 'grande' is ok, as is grande .")
        "gran caldo, gran problema, grande ala, 'grande' is ok, as is grande ."

        >>> normaliser = RegexReplace('zh-Hant_CN', path)  #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        FileNotFoundError: Could not find a locale file for locale 'zh-Hant-CN' in ...
        >>> normaliser = RegexReplace('fr', '/not/existing/dir')
        Traceback (most recent call last):
        ...
        NotADirectoryError: Expected '/not/existing/dir' to be a directory
    """

    @property
    def _normaliser(self):
        normaliser = core.Composite()
        with open(self._file) as csvfile:
            reader = csv.reader(csvfile)
            for idx, row in enumerate(reader):
                if len(row) != 2:
                    raise ValueError("Expected exactly 2 columns, got %d (in file '%s' line %d)" %
                                     (len(row), self._file, idx+1))
                normaliser.add(core.RegexReplace(row[0], row[1]))
        return normaliser

