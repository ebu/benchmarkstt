import typing
from functools import partial


class InvalidDialectError(ValueError):
    pass


class UnknownDialectError(InvalidDialectError):
    pass


class CSVParserError(ValueError):
    pass


class UnclosedQuoteError(CSVParserError):
    pass


class UnallowedQuoteError(CSVParserError):
    pass


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

# class Line(list):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#
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

    def __init__(self, file: typing.io.TextIO, dialect: Dialect):
        if not issubclass(dialect, Dialect):
            raise InvalidDialectError("Invalid dialect")
        self.line_num = 0
        self._dialect = dialect
        self._file = file

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
            return False
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
        cur_line = 0

        newlinechars = '\n\r'

        mode = MODE_FIRST
        field = []
        line = Line()

        delimiter_is_whitespace = self._dialect.delimiter in self._dialect.trimright

        def yield_line():
            nonlocal line, field, mode, delimiter_is_whitespace
            if not(mode == MODE_OUTSIDE and delimiter_is_whitespace):
                next_field()
            field = []
            _line = line
            line = Line()
            mode = MODE_FIRST
            return _line

        def next_field():
            nonlocal field, line, mode
            field = ''.join(field)
            if mode != MODE_INSIDE_QUOTED_QUOTE:
                field = self._trimright(field)

            # if not (mode == MODE_OUTSIDE and self._is_delimiter(char) and char in self._dialect.trimright):
            field = Field(field)
            # field.quoted = mode == MODE_INSIDE_QUOTED_QUOTE
            line.append(field)

            field = []
            mode = MODE_OUTSIDE

        # todo: keep proper line count
        # i = 0
        for char in readchar:
            # print('%d.%s' % (mode, char), end='\n' if (i%25)==0 else ' ')
            # i += 1
            is_newline = char in newlinechars
            if is_newline:
                cur_line += 1

            if mode == MODE_COMMENT:
                if is_newline:
                    mode = MODE_FIRST
                continue

            if mode in (MODE_OUTSIDE, MODE_FIRST):
                if self._is_ignore_left(char):
                    continue

                if mode is MODE_FIRST and self._is_comment(char):
                    mode = MODE_COMMENT
                    continue

                if self._is_quote(char):
                    mode = MODE_INSIDE_QUOTED
                    continue

                if is_newline:
                    yield yield_line()
                    continue

                if self._is_delimiter(char):
                    next_field()
                    continue

                mode = MODE_INSIDE
                field.append(char)
                continue

            if mode == MODE_INSIDE:
                if self._is_quote(char):
                    raise UnallowedQuoteError("Quote not allowed here")

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

                raise UnallowedQuoteError("Single quote inside quoted field")

            if mode == MODE_INSIDE_QUOTED:
                if self._is_quote(char):
                    mode = MODE_INSIDE_QUOTED_QUOTE
                    continue

                field.append(char)
                continue

        if mode == MODE_INSIDE_QUOTED:
            raise UnclosedQuoteError("Unexpected end")

        if mode in (MODE_INSIDE_QUOTED_QUOTE, MODE_OUTSIDE, MODE_INSIDE):
            yield yield_line()


def reader(file: typing.io.TextIO, dialect: typing.Union[None, str, Dialect]=None) -> Reader:
    if dialect is None:
        dialect = DefaultDialect
    elif type(dialect) is str:
        if dialect not in known_dialects:
            raise UnknownDialectError("Dialect %s not known" % (repr(dialect),))
        dialect = known_dialects[dialect]

    return Reader(file, dialect)



