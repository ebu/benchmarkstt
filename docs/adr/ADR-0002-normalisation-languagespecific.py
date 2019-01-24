from abc import ABC, abstractmethod


class Substitutions:
    def __init__(self, file):
        pass

    def normalise(self, text):
        pass


class Stopwords:
    def __init__(self, file):
        pass

    def normalise(self, text):
        pass


class LocaleBased(ABC):
    def __init__(self, locale, dir_path):
        self._file = None
        pass

    def normalise(self, text):
        return self._normaliser.normalise(text)

    @property
    @abstractmethod
    def _normaliser(self):
        pass


class LocaleSubstitutions(LocaleBased):
    @property
    def _normaliser(self):
        return Substitutions(self._file)


class LocaleStopwords(LocaleBased):
    @property
    def _normaliser(self):
        return Stopwords(self._file)
