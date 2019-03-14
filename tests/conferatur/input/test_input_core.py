from conferatur.input.core import PlainText
from conferatur.schema import Word, Schema

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

candide_schema = Schema(
    [Word({"text": "\"There"}), Word({"text": "is"}), Word({"text": "a"}), Word({"text": "concatenation"}),
     Word({"text": "of"}), Word({"text": "events"}), Word({"text": "in"}), Word({"text": "this"}),
     Word({"text": "best"}), Word({"text": "of"}), Word({"text": "all"}), Word({"text": "possible"}),
     Word({"text": "worlds:"}), Word({"text": "for"}), Word({"text": "if"}), Word({"text": "you"}),
     Word({"text": "had"}), Word({"text": "not"}), Word({"text": "been"}), Word({"text": "kicked"}),
     Word({"text": "out"}), Word({"text": "of"}), Word({"text": "a"}), Word({"text": "magnificent"}),
     Word({"text": "castle"}), Word({"text": "for"}), Word({"text": "love"}), Word({"text": "of"}),
     Word({"text": "Miss"}), Word({"text": "Cunegonde:"}), Word({"text": "if"}), Word({"text": "you"}),
     Word({"text": "had"}), Word({"text": "not"}), Word({"text": "been"}), Word({"text": "put"}),
     Word({"text": "into"}), Word({"text": "the"}), Word({"text": "Inquisition:"}), Word({"text": "if"}),
     Word({"text": "you"}), Word({"text": "had"}), Word({"text": "not"}), Word({"text": "walked"}),
     Word({"text": "over"}), Word({"text": "America:"}), Word({"text": "if"}), Word({"text": "you"}),
     Word({"text": "had"}), Word({"text": "not"}), Word({"text": "stabbed"}), Word({"text": "the"}),
     Word({"text": "Baron:"}), Word({"text": "if"}), Word({"text": "you"}), Word({"text": "had"}),
     Word({"text": "not"}), Word({"text": "lost"}), Word({"text": "all"}), Word({"text": "your"}),
     Word({"text": "sheep"}), Word({"text": "from"}), Word({"text": "the"}), Word({"text": "fine"}),
     Word({"text": "country"}), Word({"text": "of"}), Word({"text": "El"}), Word({"text": "Dorado:"}),
     Word({"text": "you"}), Word({"text": "would"}), Word({"text": "not"}), Word({"text": "be"}),
     Word({"text": "here"}), Word({"text": "eating"}), Word({"text": "preserved"}),
     Word({"text": "citrons"}), Word({"text": "and"}), Word({"text": "pistachio-nuts.\""}),
     Word({"text": "\"All"}), Word({"text": "that"}), Word({"text": "is"}), Word({"text": "very"}),
     Word({"text": "well,\""}), Word({"text": "answered"}), Word({"text": "Candide,"}),
     Word({"text": "\"but"}), Word({"text": "let"}), Word({"text": "us"}), Word({"text": "cultivate"}),
     Word({"text": "our"}), Word({"text": "garden.\""})])


def test_plaintext():
    assert list(PlainText(candide)) == candide_schema
    assert Schema(PlainText(candide)) == candide_schema
