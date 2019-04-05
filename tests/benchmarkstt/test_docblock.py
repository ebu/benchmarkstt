from benchmarkstt import docblock


def test_text():
    txt = """
    
    """

    assert docblock.process_rst(txt, 'text') == ''

    # todo: add more tests
