import difflib
from benchmarkstt.schema import Schema, Word
import logging


logger = logging.getLogger(__name__)


class WER:
    def compare(self, a: Schema, b: Schema):
        """
        Calculate Word Error Rate between a and b
        :param Schema a:
        :param Schema b:
        :return: float
        """

        def wrapper(schema):
            class Wrapper:
                def __init__(self, word: Word):
                    self._word = word

                def __hash__(self):
                    return hash(self._word['text'])

            return [Wrapper(row) for row in schema]

        # TODO: make a basic version working, current version is f'ed
        # TODO 2: make a proper diff implementing Hunt–McIlroy algorithm
        #         (see https://github.com/ebu/ai-benchmarking-stt/issues/30 )

        matcher = difflib.SequenceMatcher(None, wrapper(a), wrapper(b))
        codes = matcher.get_opcodes()

        counts = dict(equal=0, replace=0, insert=0, delete=0)
        for i in range(len(codes)):
            logger.debug('#%d [%s] %s -> %s', i, codes[i], a[i], b[i])
            counts[codes[i][0]] += 1

        return (counts['replace'] + counts['delete'] + counts['insert']) \
            / len(a)
