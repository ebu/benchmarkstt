from benchmarkstt.normalization import core, NormalizationComposite, File, BaseWithFileSupport, FileFactory
import logging
from io import StringIO
import pytest
from benchmarkstt.csv import UnclosedQuoteError


def test_logs(caplog):
    caplog.set_level(logging.DEBUG)
    config = '''
     # using a simple config file
     lowercase
     lowercase
     Regex ./resources/test/normalizers/doublequotestosinglequotes.regex

     # 'ni' -> 'ecky ecky ecky'
     Replace ./resources/test/normalizers/nitoeckyecky.replace
     '''
    assert core.Config._default_section is 'normalization'
    normalizer = core.Config(StringIO(config), section=core.Config.MAIN_SECTION)
    normalized = normalizer.normalize('No! Not the Knights Who Say "Ni"!')
    assert normalized == "no! not the knights who say 'ecky ecky ecky'!"

    assert len(caplog.records) == 0, \
        "logs shouldn't be propagated unless we register our own handlers"


def test_composite():
    text = 'Knights who say: NI!'
    normalizer = NormalizationComposite()
    normalizer.add(core.Lowercase())
    normalizer.add(core.Unidecode())
    assert normalizer.normalize(text) == 'knights who say: ni!'

    comp = NormalizationComposite()
    comp.add(normalizer)
    comp.add(core.Replace(' ni', ' Ekke Ekke Ekke Ekke Ptang Zoo Boing'))
    assert comp.normalize(text) == \
        'knights who say: Ekke Ekke Ekke Ekke Ptang Zoo Boing!'

    comp.add(core.Lowercase())
    assert comp.normalize(text) == \
        'knights who say: ekke ekke ekke ekke ptang zoo boing!'

    normalizer.add(core.Replace(' ni', ' nope'))
    assert comp.normalize(text) == 'knights who say: nope!'
    assert comp.normalize('Ich fälle Bäume und hüpf und spring.') == \
        'ich falle baume und hupf und spring.'


def test_lowercase():
    assert core.Lowercase().normalize('PRÁZdNÉ VLAŠToVKY') == 'prázdné vlaštovky'


def test_unidecode():
    assert core.Unidecode().normalize('Eine große europäische Schwalbe') == \
        'Eine grosse europaische Schwalbe'


def test_regex():
    normalizer = core.Regex('(scratch)', r"\1 (his arm's off)")
    assert normalizer.normalize('Tis but a scratch.') == \
        "Tis but a scratch (his arm's off)."
    assert core.Regex('ha', 'he').normalize('HA! Hahaha!') == 'HA! Hahehe!'
    assert core.Regex('(?i)(h)a', '\\1e').normalize('HAHA! Hahaha!') == \
        'HeHe! Hehehe!'
    assert core.Regex('(?msi)new.line', 'newline').normalize("New\nline") == \
        'newline'


def test_file():
    file = './resources/test/normalizers/replacecommentstest'
    normalizer = File(core.Replace, file)
    assert normalizer.normalize('# TEST\n#') == 'OKNOW'


def test_configfile():
    file = './resources/test/normalizers/configfile.conf'
    normalizer = core.Config(file, section=core.Config.MAIN_SECTION)
    assert normalizer.normalize('Ee ecky thump!') == 'aa ackY Thump!'


def test_invalidfile():
    file = './resources/test/normalizers/replacecommentstestwrongfile'

    with pytest.raises(UnclosedQuoteError) as exc:
        File(core.Replace, file)

    assert exc.value.line == 13
    assert exc.value.char == 1


def test_toomanyargs():
    file = './resources/test/normalizers/replacecommentstest'
    with pytest.raises(ValueError):
        File(core.Lowercase, file)


def test_replacewords():
    normalizer = core.ReplaceWords("ni", "ecky ecky")
    assert normalizer.normalize('Ni! We are the Knights Who Say "ni"!') == \
        'Ecky ecky! We are the Knights Who Say "ecky ecky"!'

    normalizer = core.ReplaceWords("ni", "")
    assert normalizer.normalize('Ni! We are the Knights Who Say "ni"!') == \
        '! We are the Knights Who Say ""!'

    normalizer = core.ReplaceWords("ni", ".")
    assert normalizer.normalize('Ni! We are the Knights Who Say "ni"!') == \
        '.! We are the Knights Who Say "."!'


def test_replace():
    normalizer = core.Replace('scratch', 'flesh wound')
    assert normalizer.normalize('Tis but a scratch.') == \
        'Tis but a flesh wound.'


def test_invalid_normalizer_config():
    with pytest.raises(ValueError) as e:
        core.Config(StringIO("[normalization]\nunknownnormalizer"))
    assert 'Unknown normalizer' in str(e)


def test_config_section():
    normalizer = core.Config(StringIO("test1\n[normalization]\nlowercase"), section='normalization')
    assert normalizer.normalize('ToLowerCase') == 'tolowercase'

    with pytest.raises(core.ConfigSectionNotFoundError):
        core.Config(StringIO("test1\n[normalization]\nlowercase"), section='sectiondoesntexist')


def test_base_with_file_notimplemented():
    with pytest.raises(NotImplementedError):
        BaseWithFileSupport().normalize('')


def test_filefactory():
    with pytest.raises(NotImplementedError):
        FileFactory.__getitem__(None, 'whatever')
