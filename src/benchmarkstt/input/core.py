"""
Default input formats

"""

import benchmarkstt.segmentation.core as segmenters
from benchmarkstt import input


class PlainText(input.Base):
    def __init__(self, text, segmenter=None, normalizer=None):
        if segmenter is None:
            segmenter = segmenters.Simple
        self._text = text
        self._segmenter = segmenter
        self._normalizer = normalizer

    def __iter__(self):
        return iter(self._segmenter(self._text, normalizer=self._normalizer))


class File(input.Base):
    """
    Load the input class based on a file
    """

    _extension_to_class = {
        "txt": PlainText,
        "json": None
    }

    def __init__(self, file, input_type=None, normalizer=None):
        self._normalizer = normalizer
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

        if type(input_type) is str:
            input_type = input.factory.get_class(input_type)

        self._input_class = input_type

    def __iter__(self):
        with open(self._file) as f:
            text = f.read()

        return iter(self._input_class(text, normalizer=self._normalizer))
