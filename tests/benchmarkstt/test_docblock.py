import benchmarkstt.docblock as docblock
from textwrap import dedent
import pytest


def test_text():
    txt = "  \t \t\n\n\t "

    assert docblock.process_rst(txt, 'text') == ''

    txt = '''
    .. code-block:: text

        Some block
        In samem block

        Still included


    Not anymore
'''
    print(docblock.process_rst(txt, 'text'))

    assert docblock.process_rst(txt, 'text') == """Some block
In samem block

Still included

Not anymore"""

    expected = '<blockquote>\n<pre class="code text literal-block"><code>Some block\n' \
               'In samem block\n\nStill included</code></pre>\n<p>Not anymore</p>\n' \
               '</blockquote>'
    assert docblock.process_rst(txt, 'html') == expected

    with pytest.raises(ValueError) as exc:
        docblock.process_rst(txt, 'someunknownwriter')

    assert 'Unknown writer' in str(exc)


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

        :param config: configuration text

        :example text: "He bravely turned his tail and fled"
        :example config:

            .. code-block:: text

                # using a simple config file
                Lowercase

                # it even supports comments
                # If there is a space in the argument,
                # make sure you quote it though!

                regex "y t" "Y T"

                # extraneous whitespaces are ignored
                replace   e     a

        :example return: "ha bravalY Turnad his tail and flad"
        """

    expected = docblock.Docblock(
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
        params=[
            docblock.Param(name='config', type=None, type_doc='str',
                           is_required=True, description='configuration text',
                           examples=[
                               {'text': docblock.DocblockParam(name='text', type=None,
                                                               value='He bravely turned his tail and fled'),
                                'config': docblock.DocblockParam(name='config', type=None, value=dedent('''
                                                        # using a simple config file
                                                        Lowercase

                                                        # it even supports comments
                                                        # If there is a space in the argument,
                                                        # make sure you quote it though!

                                                        regex "y t" "Y T"

                                                        # extraneous whitespaces are ignored
                                                        replace   e     a''').strip()),
                                'return': docblock.DocblockParam(name='return', type=None,
                                                                 value='ha bravalY Turnad his tail and flad')
                                }
                           ]
                           )
        ],
        result=None,
        result_type=None)

    parsed = docblock.parse(dummy_func)
    assert parsed.docs == expected.docs


def test_parse2():
    def dummy_func(self):
        """

        :return: Returns something
        """

    parsed = docblock.parse(dummy_func)
    assert parsed == docblock.Docblock(docs=':return: Returns something', params=[],
                                       result='Returns something', result_type=None)
    # todo: test the other Docblock properties as well


def test_decode_literal():
    assert docblock.decode_literal(None) == ''
    assert docblock.decode_literal('"hi!"') == 'hi!'
    assert docblock.decode_literal('58') is 58

    assert docblock.decode_literal('5.3') == 5.3
    assert docblock.decode_literal('"') == '"'
