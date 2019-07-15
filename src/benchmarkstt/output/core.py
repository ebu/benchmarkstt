from benchmarkstt import output
from benchmarkstt.schema import Schema
from collections import OrderedDict


class ReStructuredText(output.Base):
    def result(self, title, result):
        print(title)
        print('=' * len(title))
        print()

        if type(result) is float:
            print("%.6f" % (result,))
        else:
            print(result)
        print()


class MarkDown(output.Base):
    def result(self, title, result):
        print('# %s' % (title,))
        print()

        if type(result) is float:
            print("%.6f" % (result,))
        else:
            print(result)
        print()


class Json(output.Base):
    def __init__(self):
        self._line = None

    def __enter__(self):
        if self._line is not None:
            raise ValueError("Already open")
        print('[')
        self._line = 0
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._line = None
        print('\n]')

    def result(self, title, result):
        if self._line != 0:
            print(',')
        self._line += 1
        print('\t', end='')

        if isinstance(result, tuple) and hasattr(result, '_asdict'):
            result = result._asdict()

        print(Schema.dumps(OrderedDict((('title', title), ('result', result)))), end='')
