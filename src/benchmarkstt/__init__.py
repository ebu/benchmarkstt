"""
Package benchmarkstt
"""

from .__meta__ import __author__, __version__
from os import getenv


class _Settings:
    @property
    def default_encoding(self):
        return getenv('DEFAULT_ENCODING', 'UTF-8')


settings = _Settings()
