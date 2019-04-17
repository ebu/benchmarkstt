from benchmarkstt.input.core import PlainText, File
from benchmarkstt.schema import Item, Schema
import pytest

candide_file = 'tests/_data/candide.txt'
with open(candide_file) as f:
    candide = f.read()


candide_schema = [
      Item({"item": "", "type": "word", "@raw": "\n", "@segmentedOn": "\n"}),
      Item({"item": "\"There", "type": "word", "@raw": "\"There ", "@segmentedOn": " "}),
      Item({"item": "is", "type": "word", "@raw": "is ", "@segmentedOn": " "}),
      Item({"item": "a", "type": "word", "@raw": "a ", "@segmentedOn": " "}),
      Item({"item": "concatenation", "type": "word", "@raw": "concatenation ", "@segmentedOn": " "}),
      Item({"item": "of", "type": "word", "@raw": "of ", "@segmentedOn": " "}),
      Item({"item": "events", "type": "word", "@raw": "events ", "@segmentedOn": " "}),
      Item({"item": "in", "type": "word", "@raw": "in ", "@segmentedOn": " "}),
      Item({"item": "this", "type": "word", "@raw": "this ", "@segmentedOn": " "}),
      Item({"item": "best", "type": "word", "@raw": "best ", "@segmentedOn": " "}),
      Item({"item": "of", "type": "word", "@raw": "of ", "@segmentedOn": " "}),
      Item({"item": "all", "type": "word", "@raw": "all ", "@segmentedOn": " "}),
      Item({"item": "possible", "type": "word", "@raw": "possible ", "@segmentedOn": " "}),
      Item({"item": "worlds:", "type": "word", "@raw": "worlds:\n", "@segmentedOn": "\n"}),
      Item({"item": "for", "type": "word", "@raw": "for ", "@segmentedOn": " "}),
      Item({"item": "if", "type": "word", "@raw": "if ", "@segmentedOn": " "}),
      Item({"item": "you", "type": "word", "@raw": "you ", "@segmentedOn": " "}),
      Item({"item": "had", "type": "word", "@raw": "had ", "@segmentedOn": " "}),
      Item({"item": "not", "type": "word", "@raw": "not ", "@segmentedOn": " "}),
      Item({"item": "been", "type": "word", "@raw": "been ", "@segmentedOn": " "}),
      Item({"item": "kicked", "type": "word", "@raw": "kicked ", "@segmentedOn": " "}),
      Item({"item": "out", "type": "word", "@raw": "out ", "@segmentedOn": " "}),
      Item({"item": "of", "type": "word", "@raw": "of ", "@segmentedOn": " "}),
      Item({"item": "a", "type": "word", "@raw": "a ", "@segmentedOn": " "}),
      Item({"item": "magnificent", "type": "word", "@raw": "magnificent ", "@segmentedOn": " "}),
      Item({"item": "castle", "type": "word", "@raw": "castle ", "@segmentedOn": " "}),
      Item({"item": "for", "type": "word", "@raw": "for ", "@segmentedOn": " "}),
      Item({"item": "love", "type": "word", "@raw": "love ", "@segmentedOn": " "}),
      Item({"item": "of", "type": "word", "@raw": "of\n", "@segmentedOn": "\n"}),
      Item({"item": "Miss", "type": "word", "@raw": "Miss ", "@segmentedOn": " "}),
      Item({"item": "Cunegonde:", "type": "word", "@raw": "Cunegonde: ", "@segmentedOn": " "}),
      Item({"item": "if", "type": "word", "@raw": "if ", "@segmentedOn": " "}),
      Item({"item": "you", "type": "word", "@raw": "you ", "@segmentedOn": " "}),
      Item({"item": "had", "type": "word", "@raw": "had ", "@segmentedOn": " "}),
      Item({"item": "not", "type": "word", "@raw": "not ", "@segmentedOn": " "}),
      Item({"item": "been", "type": "word", "@raw": "been ", "@segmentedOn": " "}),
      Item({"item": "put", "type": "word", "@raw": "put ", "@segmentedOn": " "}),
      Item({"item": "into", "type": "word", "@raw": "into ", "@segmentedOn": " "}),
      Item({"item": "the", "type": "word", "@raw": "the ", "@segmentedOn": " "}),
      Item({"item": "Inquisition:", "type": "word", "@raw": "Inquisition: ", "@segmentedOn": " "}),
      Item({"item": "if", "type": "word", "@raw": "if ", "@segmentedOn": " "}),
      Item({"item": "you", "type": "word", "@raw": "you ", "@segmentedOn": " "}),
      Item({"item": "had", "type": "word", "@raw": "had\n", "@segmentedOn": "\n"}),
      Item({"item": "not", "type": "word", "@raw": "not ", "@segmentedOn": " "}),
      Item({"item": "walked", "type": "word", "@raw": "walked ", "@segmentedOn": " "}),
      Item({"item": "over", "type": "word", "@raw": "over ", "@segmentedOn": " "}),
      Item({"item": "America:", "type": "word", "@raw": "America: ", "@segmentedOn": " "}),
      Item({"item": "if", "type": "word", "@raw": "if ", "@segmentedOn": " "}),
      Item({"item": "you", "type": "word", "@raw": "you ", "@segmentedOn": " "}),
      Item({"item": "had", "type": "word", "@raw": "had ", "@segmentedOn": " "}),
      Item({"item": "not", "type": "word", "@raw": "not ", "@segmentedOn": " "}),
      Item({"item": "stabbed", "type": "word", "@raw": "stabbed ", "@segmentedOn": " "}),
      Item({"item": "the", "type": "word", "@raw": "the ", "@segmentedOn": " "}),
      Item({"item": "Baron:", "type": "word", "@raw": "Baron: ", "@segmentedOn": " "}),
      Item({"item": "if", "type": "word", "@raw": "if ", "@segmentedOn": " "}),
      Item({"item": "you", "type": "word", "@raw": "you ", "@segmentedOn": " "}),
      Item({"item": "had", "type": "word", "@raw": "had\n", "@segmentedOn": "\n"}),
      Item({"item": "not", "type": "word", "@raw": "not ", "@segmentedOn": " "}),
      Item({"item": "lost", "type": "word", "@raw": "lost ", "@segmentedOn": " "}),
      Item({"item": "all", "type": "word", "@raw": "all ", "@segmentedOn": " "}),
      Item({"item": "your", "type": "word", "@raw": "your ", "@segmentedOn": " "}),
      Item({"item": "sheep", "type": "word", "@raw": "sheep ", "@segmentedOn": " "}),
      Item({"item": "from", "type": "word", "@raw": "from ", "@segmentedOn": " "}),
      Item({"item": "the", "type": "word", "@raw": "the ", "@segmentedOn": " "}),
      Item({"item": "fine", "type": "word", "@raw": "fine ", "@segmentedOn": " "}),
      Item({"item": "country", "type": "word", "@raw": "country ", "@segmentedOn": " "}),
      Item({"item": "of", "type": "word", "@raw": "of ", "@segmentedOn": " "}),
      Item({"item": "El", "type": "word", "@raw": "El ", "@segmentedOn": " "}),
      Item({"item": "Dorado:", "type": "word", "@raw": "Dorado: ", "@segmentedOn": " "}),
      Item({"item": "you", "type": "word", "@raw": "you ", "@segmentedOn": " "}),
      Item({"item": "would", "type": "word", "@raw": "would\n", "@segmentedOn": "\n"}),
      Item({"item": "not", "type": "word", "@raw": "not ", "@segmentedOn": " "}),
      Item({"item": "be", "type": "word", "@raw": "be ", "@segmentedOn": " "}),
      Item({"item": "here", "type": "word", "@raw": "here ", "@segmentedOn": " "}),
      Item({"item": "eating", "type": "word", "@raw": "eating ", "@segmentedOn": " "}),
      Item({"item": "preserved", "type": "word", "@raw": "preserved ", "@segmentedOn": " "}),
      Item({"item": "citrons", "type": "word", "@raw": "citrons ", "@segmentedOn": " "}),
      Item({"item": "and", "type": "word", "@raw": "and ", "@segmentedOn": " "}),
      Item({"item": "pistachio-nuts.\"", "type": "word", "@raw": "pistachio-nuts.\"\n\n", "@segmentedOn": "\n\n"}),
      Item({"item": "\"All", "type": "word", "@raw": "\"All ", "@segmentedOn": " "}),
      Item({"item": "that", "type": "word", "@raw": "that ", "@segmentedOn": " "}),
      Item({"item": "is", "type": "word", "@raw": "is ", "@segmentedOn": " "}),
      Item({"item": "very", "type": "word", "@raw": "very ", "@segmentedOn": " "}),
      Item({"item": "well,\"", "type": "word", "@raw": "well,\" ", "@segmentedOn": " "}),
      Item({"item": "answered", "type": "word", "@raw": "answered ", "@segmentedOn": " "}),
      Item({"item": "Candide,", "type": "word", "@raw": "Candide, ", "@segmentedOn": " "}),
      Item({"item": "\"but", "type": "word", "@raw": "\"but ", "@segmentedOn": " "}),
      Item({"item": "let", "type": "word", "@raw": "let ", "@segmentedOn": " "}),
      Item({"item": "us", "type": "word", "@raw": "us ", "@segmentedOn": " "}),
      Item({"item": "cultivate", "type": "word", "@raw": "cultivate ", "@segmentedOn": " "}),
      Item({"item": "our", "type": "word", "@raw": "our\n", "@segmentedOn": "\n"}),
      Item({"item": "garden.\"", "type": "word", "@raw": "garden.\"\n", "@segmentedOn": "\n"}),
  ]


@pytest.mark.parametrize('cls,args', [
    [PlainText, [candide]],
    [File, [candide_file]],
    [File, [candide_file, 'infer']],
    [File, [candide_file, 'plaintext']],
])
def test_file(cls, args):
    assert list(cls(*args)) == candide_schema
    assert Schema(cls(*args)) == candide_schema


def test_exceptions():
    with pytest.raises(ValueError) as e:
        File('noextension')
    assert 'without an extension' in str(e)

    with pytest.raises(ValueError) as e:
        File('unknownextension.thisisntknowm')
    assert 'thisisntknowm' in str(e)
