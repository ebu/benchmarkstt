from benchmarkstt.docblock import *
from textwrap import dedent


def test_text():
    txt = "  \t \t\n\n\t "

    assert process_rst(txt, 'text') == ''

    txt = '''
    .. code-block:: text

        Some block
        In samem block

        Still included


    Not anymore
'''
    print(process_rst(txt, 'text'))

    assert process_rst(txt, 'text') == """Some block
In samem block

Still included

Not anymore"""


def test_parse():
    def dummy_func(config):
        """
        The normalization rules are applied top-to-bottom and follow this format:

        .. code-block:: text

            Normalizer1 arg1 "arg 2"
            # This is a comment

            Normalizer2
            # (Normalizer2 has no arguments)
            Normalizer3 "This is argument 1
            Spanning multiple lines
            " "argument 2"
            Normalizer4 "argument with double quote ("")"

        :param str config: configuration text

        :example text: "He bravely turned his tail and fled"
        :example config:

            .. code-block:: text

                # using a simple config file
                Lowercase

                # it even supports comments
                # If there is a space in the argument,
                # make sure you quote it though!

                regexreplace "y t" "Y T"

                # extraneous whitespaces are ignored
                replace   e     a

        :example return: "ha bravalY Turnad his tail and flad"
        """

    expected = Docblock(
        docs=dedent('''
        The normalization rules are applied top-to-bottom and follow this format:

        .. code-block:: text

            Normalizer1 arg1 "arg 2"
            # This is a comment

            Normalizer2
            # (Normalizer2 has no arguments)
            Normalizer3 "This is argument 1
            Spanning multiple lines
            " "argument 2"
            Normalizer4 "argument with double quote ("")"
        ''').strip(),
        params=[Param(name='config', type=None, type_doc='str', is_required=True, description='configuration text',
                      examples=[
                          {'text': DocblockParam(name='text', type=None, value='He bravely turned his tail and fled'),
                           'config': DocblockParam(name='config', type=None,
                                                   value=dedent('''
                                                   # using a simple config file
                                                   Lowercase

                                                   # it even supports comments
                                                   # If there is a space in the argument,
                                                   # make sure you quote it though!

                                                   regexreplace "y t" "Y T"

                                                   # extraneous whitespaces are ignored
                                                   replace   e     a''').strip()),
                           'return': DocblockParam(name='return', type=None,
                                                   value='ha bravalY Turnad his tail and flad')
                           }
                      ]
                      )
                ],
        result=None,
        result_type=None)

    parsed = parse(dummy_func)
    assert parsed.docs == expected.docs
    # assert parsed.params == expected.params
