"""
Module providing our own CSV file parser with support for whitespace trimming, empty lines filtering and comment lines
"""

import typing
import sys
from functools import partial
from benchmarkstt import DeferredList, make_printable


class InvalidDialectError(ValueError):
    """An invalid dialect was supplied"""


class UnknownDialectError(ValueError):
    """An unknown dialect was requested"""


class CSVParserError(ValueError):
    """Some error occured while attempting to parse the file"""

    def __init__(self, message, line, char, index):
        self.message = message
        self.line = line
        self.char = char
        self.index = index


class UnclosedQuoteError(CSVParserError):
    """A quote wasn't properly closed"""


class UnallowedQuoteError(CSVParserError):
    """A quote is not allowed there"""


class Dialect:
    delimiter = None
    quotechar = None
    commentchar = None
    trimleft = None
    trimright = None


class DefaultDialect(Dialect):
    delimiter = ','
    quotechar = '"'
    commentchar = '#'
    trimleft = ' \t\n\r'
    trimright = trimleft
    ignoreemptylines = True


class WhitespaceDialect(DefaultDialect):
    delimiter = ' \t'


known_dialects = {
    "default": DefaultDialect,
    "whitespace": WhitespaceDialect
}

MODE_FIRST = 0
MODE_OUTSIDE = 1
MODE_INSIDE = 2
MODE_INSIDE_QUOTED = 3
MODE_INSIDE_QUOTED_QUOTE = 4
MODE_COMMENT = 5

Line = list
Field = str


class Line(list):
    @property
    def lineno(self):
        return self.__dict__['lineno']

# don't really know if it's quoted atm
# class Field(str, object):
#     @property
#     def quoted(self):
#         return self.__dict__['quoted']
#
#     @quoted.setter
#     def quoted(self, value):
#         self.__dict__['quoted'] = bool(value)


class Reader:
    """
    CSV-like file reader with support for comment chars, ignoring empty lines
    and whitespace trimming on both sides of each field.

    """

    def __init__(self, file: typing.io.TextIO, dialect: Dialect, debug=None):
        if not issubclass(dialect, Dialect):
            raise InvalidDialectError("Invalid dialect", dialect)
        self.line_num = 0
        self._dialect = dialect
        self._file = file
        self._debug = bool(debug)

    def _trimright(self, data: str):
        chars = self._dialect.trimright
        if chars is None:
            return data
        return data.rstrip(chars)

    def _is_ignore_left(self, char: str):
        if self._dialect.trimleft is None:
            return False
        return char in self._dialect.trimleft

    def _is_ignore_right(self, char: str):
        if self._dialect.trimright is None:
            # currently no dialect with no trimright
            return False  # pragma: nocover
        return char in self._dialect.trimright

    def _is_comment(self, char: str):
        if self._dialect.commentchar is None:
            return False
        return char in self._dialect.commentchar

    def _is_quote(self, char: str):
        if self._dialect.quotechar is None:
            return False
        return char == self._dialect.quotechar

    def _is_delimiter(self, char: str):
        return char in self._dialect.delimiter

    def __iter__(self):
        readchar = iter(partial(self._file.read, 1), '')
        cur_line = 1

        if self._debug:
            current_module = sys.modules[__name__]
            # print the color key the different modes
            print('MODES: ', end='')
            print(' '.join(['\033[1;%d;40m%s\033[0;0m' % (32 + getattr(current_module, name), name[5:])
                            for name in dir(current_module)
                            if name.startswith('MODE_')
                            ]))

            def debug(txt='', args=tuple(), **kwargs):
                if type(args) is not tuple:
                    args = tuple(DeferredList(args))
                print(txt % args, **kwargs)
                pass
        else:
            def debug(*args, **kwargs):
                pass

        newlinechars = '\n\r'

        mode = MODE_FIRST
        field = []
        line = Line()

        if self._dialect.trimright is not None:
            delimiter_is_whitespace = self._dialect.delimiter in self._dialect.trimright
        else:
            delimiter_is_whitespace = False

        def yield_line():
            nonlocal line, field, mode, delimiter_is_whitespace, is_newline, cur_line
            if not(mode == MODE_OUTSIDE and delimiter_is_whitespace):
                next_field()
            field = []
            _line = line
            _line.__dict__['lineno'] = cur_line
            line = Line()
            mode = MODE_FIRST
            return _line

        def next_field():
            nonlocal field, line, mode
            field = ''.join(field)
            if mode != MODE_INSIDE_QUOTED_QUOTE:
                field = self._trimright(field)

            field = Field(field)
            line.append(field)

            field = []
            mode = MODE_OUTSIDE

        cur_char = 0
        last_quote_line = None
        last_quote_char = None
        last_quote_idx = None
        idx = 0
        for char in readchar:
            cur_char += 1
            idx += 1

            # print char to stdout with color defining mode
            debug('\033[1;%d;40m%s\033[0;0m', lambda: (32+mode, make_printable(char)), end='')

            is_newline = char in newlinechars
            if is_newline:
                cur_line += 1
                cur_char = 0

            if mode == MODE_COMMENT:
                if is_newline:
                    mode = MODE_FIRST
                continue

            if mode in (MODE_OUTSIDE, MODE_FIRST):
                if is_newline:
                    if mode != MODE_FIRST:
                        yield yield_line()
                    continue

                if self._is_ignore_left(char):
                    continue

                if self._is_comment(char):
                    if mode is MODE_OUTSIDE:
                        yield yield_line()
                    mode = MODE_COMMENT
                    continue

                if self._is_quote(char):
                    mode = MODE_INSIDE_QUOTED
                    last_quote_line = cur_line
                    last_quote_char = cur_char
                    last_quote_idx = idx
                    continue

                if self._is_delimiter(char):
                    next_field()
                    continue

                mode = MODE_INSIDE
                field.append(char)
                continue

            if mode == MODE_INSIDE:
                if self._is_quote(char):
                    raise UnallowedQuoteError("Quote not allowed here", cur_line, cur_char, idx)

                if is_newline:
                    yield yield_line()
                    continue

                if self._is_delimiter(char):
                    next_field()
                    continue

                field.append(char)
                continue

            if mode == MODE_INSIDE_QUOTED_QUOTE:
                if self._is_quote(char):
                    field.append(char)
                    mode = MODE_INSIDE_QUOTED
                    continue

                if self._is_delimiter(char):
                    next_field()
                    continue

                if is_newline:
                    yield yield_line()
                    continue

                if not delimiter_is_whitespace:
                    if self._is_ignore_right(char):
                        continue
                    if self._is_comment(char):
                        yield yield_line()
                        mode = MODE_COMMENT
                        continue

                raise UnallowedQuoteError("Single quote inside quoted field", cur_line, cur_char, idx)

            if mode == MODE_INSIDE_QUOTED:
                if self._is_quote(char):
                    mode = MODE_INSIDE_QUOTED_QUOTE
                    continue

                field.append(char)
                continue

        debug()

        if mode == MODE_INSIDE_QUOTED:
            raise UnclosedQuoteError("Unexpected end", last_quote_line, last_quote_char, last_quote_idx)

        if mode in (MODE_INSIDE_QUOTED_QUOTE, MODE_OUTSIDE, MODE_INSIDE):
            yield yield_line()


def reader(file: typing.io.TextIO, dialect: typing.Union[None, str, Dialect] = None, **kwargs) -> Reader:
    if dialect is None:
        dialect = DefaultDialect
    elif type(dialect) is str:
        if dialect not in known_dialects:
            raise UnknownDialectError("Dialect not known", dialect)
        dialect = known_dialects[dialect]

    return Reader(file, dialect, **kwargs)
