"""
Some helper methods that can be re-used across submodules
"""


def make_printable(char):
    """
    Return printable representation of ascii/utf-8 control characters

    :param char:
    :return str:
    """
    if not len(char):
        return ''
    if len(char) > 1:
        return ''.join(list(map(make_printable, char)))

    codepoint = ord(char)
    if 0x00 <= codepoint <= 0x1f or 0x7f <= codepoint <= 0x9f:
        return chr(0x2400 | codepoint)

    return char if char != ' ' else '·'
