"""
Default input formats

Each format class should be accessible as iterator, each iteration should return a Word, so the input format is
essentially usable and can be easily converted to a :py:class:`benchmarkstt.schema.Schema`
"""

import benchmarkstt.segmentation.core as segmenters
from sys import modules
import inspect


def is_cls(cls):
    return inspect.isclass(cls) and hasattr(cls, '__iter__')


class PlainText:
    def __init__(self, text, segmenter=None):
        if segmenter is None:
            segmenter = segmenters.Simple
        self._text = text
        self._segmenter = segmenter

    def __iter__(self):
        return iter(self._segmenter(self._text))


class File:
    """
    Load the input class based on a file
    """

    _extension_to_class = {
        "txt": PlainText,
        "json": None
    }

    def __init__(self, file, input_type=None):
        if input_type is None or input_type == 'infer':
            if '.' not in file:
                raise ValueError('Cannot infer input file type of files without an extension')

            extension = file.rsplit('.', 1)[1].lower()
            if extension not in self._extension_to_class:
                raise ValueError('Cannot infer input file type for files of extension %s' % (extension,))

            input_type = self._extension_to_class[extension]

        with open(file):
            """Just checks that file is readable..."""

        self._file = file

        self._input_class = self._get_cls(input_type)

    @staticmethod
    def _get_cls(cls_or_name):
        if type(cls_or_name) is str:
            m = [cls for clsname, cls in inspect.getmembers(modules[__name__], is_cls)
                 if clsname.lower() == cls_or_name.lower]

            if len(m) == 0:
                raise ValueError("Could not find a possible input type for '%s'" % (cls_or_name,))

            if len(m) > 1:
                raise ValueError("More than one possible input type for '%s'" % (cls_or_name,))

            cls_or_name = m[0]

        return cls_or_name

    def __iter__(self):
        with open(self._file) as f:
            text = f.read()

        return iter(self._input_class(text))
