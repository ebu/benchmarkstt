import difflib
from benchmarkstt.schema import Schema
import logging


logger = logging.getLogger(__name__)


class WER:
    """
    Item Error Rate, basically defined as:

    .. code-block :: text

        insertions + deletions + substitions
        ------------------------------------
             number of reference words

    See: https://en.wikipedia.org/wiki/Word_error_rate
    """

    MODE_STRICT = 0
    MODE_HUNT = 1
    MODE_DIFFLIBRATIO = 2

    def __init__(self, mode=None):
        if mode is None:
            mode = self.MODE_STRICT
        self._mode = mode

    def compare(self, ref: Schema, hyp: Schema):
        """
        :param Schema ref:
        :param Schema hyp:
        :return: float
        """

        # TODO: make a proper diff implementing Hunt–McIlroy algorithm
        #      (see https://github.com/ebu/ai-benchmarking-stt/issues/30 )

        # TODO: proper documenting of different modes

        def traversible(schema):
            return [word['item'] for word in schema]

        matcher = difflib.SequenceMatcher(a=traversible(ref),
                                          b=traversible(hyp),
                                          autojunk=False)

        if self._mode == self.MODE_DIFFLIBRATIO:
            return matcher.ratio()

        codes = matcher.get_opcodes()

        counts = dict(equal=0, replace=0, insert=0, delete=0)

        for code in codes:
            counts[code[0]] += (code[2] - code[1]) if code[0] != 'insert' else code[4] - code[3]

        logger.debug(counts)

        if self._mode == self.MODE_HUNT:
            changes = counts['replace'] + counts['delete']/2 + counts['insert']/2
        else:
            changes = counts['replace'] + counts['delete'] + counts['insert']

        assert len(ref) == counts['replace'] + counts['delete'] + counts['equal']
        return changes / len(ref)
