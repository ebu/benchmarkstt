from difflib import SequenceMatcher
from benchmarkstt.diff import Base


class RatcliffObershelp(SequenceMatcher, Base):
    def __init__(self, a, b, *args, **kwargs):
        if 'autojunk' not in kwargs:
            kwargs['autojunk'] = False
        super().__init__(a=a, b=b, *args, **kwargs)
