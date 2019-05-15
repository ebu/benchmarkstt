from benchmarkstt.normalization.core import *
from benchmarkstt.normalization import NormalizationComposite, File
import logging


def itest_logs(caplog):
    caplog.set_level(logging.DEBUG)
    config = '''
     # using a simple config file
     lowercase
     lowercase
     # Let's replace double quotes with single quotes (note wrapping in double
     # quotes, to allow the use of double quotes in an argument.
     Regex "[""]" '
     # A space in the argument: wrap in double quotes as well
     Replace 'ni' "'ecky ecky ecky'"
     '''
    normalizer = Config(config)
    normalized = normalizer.normalize('No! Not the Knights Who Say "Ni"!')
    assert normalized == "no! not the knights who say 'ecky ecky ecky'!"

    assert len(caplog.records) == 0, \
        "logs shouldn't be propagated unless we register our own handlers"


def test_composite():
    text = 'Knights who say: NI!'
    normalizer = NormalizationComposite()
    normalizer.add(Lowercase())
    normalizer.add(Unidecode())
    assert normalizer.normalize(text) == 'knights who say: ni!'

    comp = NormalizationComposite()
    comp.add(normalizer)
    comp.add(Replace(' ni', ' Ekke Ekke Ekke Ekke Ptang Zoo Boing'))
    assert comp.normalize(text) == \
        'knights who say: Ekke Ekke Ekke Ekke Ptang Zoo Boing!'

    comp.add(Lowercase())
    assert comp.normalize(text) == \
        'knights who say: ekke ekke ekke ekke ptang zoo boing!'

    normalizer.add(Replace(' ni', ' nope'))
    assert comp.normalize(text) == 'knights who say: nope!'
    assert comp.normalize('Ich fälle Bäume und hüpf und spring.') == \
        'ich falle baume und hupf und spring.'


def test_lowercase():
    assert Lowercase().normalize('PRÁZdNÉ VLAŠToVKY') == 'prázdné vlaštovky'


def test_unidecode():
    assert Unidecode().normalize('Eine große europäische Schwalbe') == \
        'Eine grosse europaische Schwalbe'


def test_regex():
    normalizer = Regex('(scratch)', r"\1 (his arm's off)")
    assert normalizer.normalize('Tis but a scratch.') == \
        "Tis but a scratch (his arm's off)."
    assert Regex('ha', 'he').normalize('HA! Hahaha!') == 'HA! Hahehe!'
    assert Regex('(?i)(h)a', r'\1e').normalize('HAHA! Hahaha!') == \
        'HeHe! Hehehe!'
    assert Regex('(?msi)new.line', 'newline').normalize("New\nline") == \
        'newline'


def test_file():
    file = './resources/test/normalizers/replacecommentstest'
    normalizer = File(Replace, file)
    assert normalizer.normalize('# TEST\n#') == 'OKNOW'


def test_configfile():
    file = './resources/test/normalizers/configfile.conf'
    normalizer = Config(file)
    assert normalizer.normalize('Ee ecky thump!') == 'aa ackY Thump!'


def test_replacewords():
    normalizer = ReplaceWords("ni", "ecky ecky")
    assert normalizer.normalize('Ni! We are the Knights Who Say "ni"!') == \
        'Ecky ecky! We are the Knights Who Say "ecky ecky"!'

    normalizer = ReplaceWords("ni", "")
    assert normalizer.normalize('Ni! We are the Knights Who Say "ni"!') == \
        '! We are the Knights Who Say ""!'

    normalizer = ReplaceWords("ni", ".")
    assert normalizer.normalize('Ni! We are the Knights Who Say "ni"!') == \
        '.! We are the Knights Who Say "."!'


def test_replace():
    normalizer = Replace('scratch', 'flesh wound')
    assert normalizer.normalize('Tis but a scratch.') == \
        'Tis but a flesh wound.'

#
# def test_localizedfile():
#     path = './resources/test/normalizers/configfile'
#     normalizer = LocalizedFile('Config', 'en_UK', path)
#     assert normalizer.normalize("𝔊𝔯𝔞𝔫𝔡𝔢 𝔖𝔞𝔰𝔰𝔬 𝔡'ℑ𝔱𝔞𝔩𝔦𝔞") == \
#         "gran sasso d'italia"
