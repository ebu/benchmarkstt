from benchmarkstt.input import PlainText
from benchmarkstt.schema import Word, Schema

candide = '''
"There is a concatenation of events in this best of all possible worlds:
for if you had not been kicked out of a magnificent castle for love of
Miss Cunegonde: if you had not been put into the Inquisition: if you had
not walked over America: if you had not stabbed the Baron: if you had
not lost all your sheep from the fine country of El Dorado: you would
not be here eating preserved citrons and pistachio-nuts."

"All that is very well," answered Candide, "but let us cultivate our
garden."
'''

candide_schema = Schema(map(Word,
                            [{"text": "\"There"}, {"text": "is"},
                             {"text": "a"},
                             {"text": "concatenation"},
                             {"text": "of"}, {"text": "events"},
                             {"text": "in"},
                             {"text": "this"},
                             {"text": "best"}, {"text": "of"}, {"text": "all"},
                             {"text": "possible"},
                             {"text": "worlds:"}, {"text": "for"},
                             {"text": "if"},
                             {"text": "you"},
                             {"text": "had"}, {"text": "not"},
                             {"text": "been"},
                             {"text": "kicked"},
                             {"text": "out"}, {"text": "of"}, {"text": "a"},
                             {"text": "magnificent"},
                             {"text": "castle"}, {"text": "for"},
                             {"text": "love"},
                             {"text": "of"},
                             {"text": "Miss"}, {"text": "Cunegonde:"},
                             {"text": "if"},
                             {"text": "you"},
                             {"text": "had"}, {"text": "not"},
                             {"text": "been"},
                             {"text": "put"},
                             {"text": "into"}, {"text": "the"},
                             {"text": "Inquisition:"},
                             {"text": "if"},
                             {"text": "you"}, {"text": "had"}, {"text": "not"},
                             {"text": "walked"},
                             {"text": "over"}, {"text": "America:"},
                             {"text": "if"},
                             {"text": "you"},
                             {"text": "had"}, {"text": "not"},
                             {"text": "stabbed"},
                             {"text": "the"},
                             {"text": "Baron:"}, {"text": "if"},
                             {"text": "you"},
                             {"text": "had"},
                             {"text": "not"}, {"text": "lost"},
                             {"text": "all"},
                             {"text": "your"},
                             {"text": "sheep"}, {"text": "from"},
                             {"text": "the"},
                             {"text": "fine"},
                             {"text": "country"}, {"text": "of"},
                             {"text": "El"},
                             {"text": "Dorado:"},
                             {"text": "you"}, {"text": "would"},
                             {"text": "not"},
                             {"text": "be"},
                             {"text": "here"}, {"text": "eating"},
                             {"text": "preserved"},
                             {"text": "citrons"}, {"text": "and"},
                             {"text": "pistachio-nuts.\""},
                             {"text": "\"All"}, {"text": "that"},
                             {"text": "is"},
                             {"text": "very"},
                             {"text": "well,\""}, {"text": "answered"},
                             {"text": "Candide,"},
                             {"text": "\"but"}, {"text": "let"},
                             {"text": "us"},
                             {"text": "cultivate"},
                             {"text": "our"}, {"text": "garden.\""}
                             ]))


def test_plaintext():
    assert list(PlainText(candide)) == candide_schema
    assert Schema(PlainText(candide)) == candide_schema
