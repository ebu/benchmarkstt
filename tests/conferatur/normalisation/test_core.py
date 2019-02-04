from conferatur.normalisation.core import *


def test_config():
    config = '''
     # using a simple config file
     lowercase
     # Let's replace double quotes with single quotes (note wrapping in double quotes,
     # to allow the use of double quotes in an argument.
     RegexReplace "[""]" '
     # A space in the argument: wrap in double quotes as well
     Replace 'ni' "'ecky ecky ecky'"
     '''
    normaliser = Config(config)
    normalised = normaliser.normalise('No! Not the Knights Who Say "Ni"!')
    assert normalised == "no! not the knights who say 'ecky ecky ecky'!"

    # Lets replace spaces with a newline (without using regex), demonstrating multiline arguments
    # also note that the normaliser name is case-insensitive

    config = 'replace " " "\n"'
    normaliser = Config(config)
    normalised = normaliser.normalise("None shall pass.")
    assert normalised == 'None\nshall\npass.'
    normalised = Config('Replace     t      " T "').normalise("test")
    assert normalised == ' T es T '

    # todo
    # Loading a custom normaliser that wraps the text in square brackets
    # Config('resources.test.normalisers.testnormaliser').normalise('test')
    #


def test_composite():
    text = 'Knights who say: NI!'
    normaliser = Composite()
    normaliser.add(Lowercase())
    normaliser.add(Unidecode())
    assert normaliser.normalise(text) == 'knights who say: ni!'

    comp = Composite()
    comp.add(normaliser)
    comp.add(Replace(' ni', ' Ekke Ekke Ekke Ekke Ptang Zoo Boing'))
    assert comp.normalise(text) == 'knights who say: Ekke Ekke Ekke Ekke Ptang Zoo Boing!'

    comp.add(Lowercase())
    assert comp.normalise(text) == 'knights who say: ekke ekke ekke ekke ptang zoo boing!'

    normaliser.add(Replace(' ni', ' nope'))
    assert comp.normalise(text) == 'knights who say: nope!'
    assert comp.normalise('Ich fälle Bäume und hüpf und spring.') == 'ich falle baume und hupf und spring.'


def test_lowercase():
    assert Lowercase().normalise('PRÁZdNÉ VLAŠToVKY') == 'prázdné vlaštovky'


def test_unicode():
    assert Unidecode().normalise('Eine große europäische Schwalbe') == 'Eine grosse europaische Schwalbe'


def test_alphanumericunicode():
    assert AlphaNumericUnicode().normalise("Das, öder die Flipper-Wåld Gespütt!") == 'DasöderdieFlipperWåldGespütt'


def test_alphanumeric():
    assert AlphaNumeric().normalise("She turned me into a newt.") == 'Sheturnedmeintoanewt'
    assert AlphaNumeric().normalise("Das, öder die Flipper-Wåld Gespütt!") == 'DasderdieFlipperWldGesptt'


def test_regexreplace():
    normaliser = RegexReplace('(scratch)', r"\1 (his arm's off)")
    assert normaliser.normalise('Tis but a scratch.') == "Tis but a scratch (his arm's off)."
    assert RegexReplace('ha', 'he').normalise('HA! Hahaha!') == 'HA! Hahehe!'
    assert RegexReplace('(?i)(h)a', r'\1e').normalise('HAHA! Hahaha!') == 'HeHe! Hehehe!'
    assert RegexReplace('(?msi)new.line', 'newline').normalise("New\nline") == 'newline'


def test_file():
    file = './resources/test/normalisers/replacecommentstest'
    normaliser = File('replace', file)
    assert normaliser.normalise('# TEST\n#') == 'OKNOW'


def test_configfile():
    file = './resources/test/normalisers/configfile.conf'
    normaliser = ConfigFile(file)
    assert normaliser.normalise('Ee ecky thump!') == 'aa ackY Thump!'


def test_replacewords():
    normaliser = ReplaceWords("ni", "ecky ecky")
    assert normaliser.normalise('Ni! We are the Knights Who Say "ni"!') == \
        'Ecky ecky! We are the Knights Who Say "ecky ecky"!'


def test_replace():
    normaliser = Replace('scratch', 'flesh wound')
    assert normaliser.normalise('Tis but a scratch.') == 'Tis but a flesh wound.'


def test_localisedfile():
    path = './resources/test/normalisers/configfile'
    normaliser = LocalisedFile('Config', 'en_UK', path)
    assert normaliser.normalise("𝔊𝔯𝔞𝔫𝔡𝔢 𝔖𝔞𝔰𝔰𝔬 𝔡'ℑ𝔱𝔞𝔩𝔦𝔞") == "gran sasso d'italia"