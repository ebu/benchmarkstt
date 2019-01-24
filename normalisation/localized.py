"""
Normalisation based on locale
"""

from abc import ABC, abstractmethod
from . import core
import os
from langcodes import best_match, standardize_tag
import csv


class AbstractLocale(ABC):
    def __init__(self, locale, path):
        self._file = self.choose_file(locale, path)

    @staticmethod
    def choose_file(locale, path):
        if not os.path.isdir(path):
            raise NotADirectoryError("Expected '$s' to be a directory")
        files = {standardize_tag(file): file
                 for file in os.listdir(path)
                 if os.path.isfile(os.path.join(path, file))}

        locale = standardize_tag(locale)
        match = best_match(locale, files.keys())[0]
        if match == 'und':
            raise FileNotFoundError("Could not find a locale file for locale '%s' in '%s'" % (locale, path))
        return os.path.join(path, files[match])

    def normalise(self, text):
        return self._normaliser.normalise(text)

    @property
    @abstractmethod
    def _normaliser(self):
        pass


class RegexReplace(AbstractLocale):
    """
    >>> from os.path import dirname, realpath, join
    >>> path = dirname(dirname(realpath(__file__)))
    >>> path = join(path, 'resources', 'normalisers', 'test', 'regexreplace')
    >>>
    >>> normaliser = RegexReplace('en_UK', path)
    >>> normaliser.normalise("You're like a German par-a-keet")
    'Youre like a German parrot'
    >>> normaliser = RegexReplace('it', path)
    >>> normaliser.normalise("grande caldo, grande problema, grande ala")
    'gran caldo, gran problema, grande ala'
    """

    @property
    def _normaliser(self):
        normaliser = core.Composite()
        with open(self._file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) != 2:
                    raise ValueError("Expected exactly 2 columns")
                normaliser.add(core.RegexReplace(row[0], row[1]))
        return normaliser

