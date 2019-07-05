from benchmarkstt.__meta__ import __version__
from collections import OrderedDict
import pytest
import json
import sys

pytestmark = pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")

benchmarkparams = {
    "ref": "Hello darkness my OLD friend",
    "hyp": "Hello darkness my old foe",
    "config": "[normalization]\n# using a simple config file\nLowercase"
}

benchmarklogs = [
    OrderedDict(
        title='Reference',
        stack=[
            "Config",
            "[normalization]",
            "Lowercase"
        ],
        diff="<span class=\"delete\">H</span><span class=\"insert\">h</span>ello darkness "
             "my <span class=\"delete\">OLD</span><span class=\"insert\">old</span> friend"
    ),
    OrderedDict(
        title='Reference',
        stack=[
            "Config",
            "[normalization]"
        ],
        diff="<span class=\"delete\">H</span><span class=\"insert\">h</span>ello darkness my "
             "<span class=\"delete\">OLD</span><span class=\"insert\">old</span> friend"
    ),
    OrderedDict(
        title='Reference',
        stack=[
            "Config"
        ],
        diff="<span class=\"delete\">H</span><span class=\"insert\">h</span>ello darkness my "
             "<span class=\"delete\">OLD</span><span class=\"insert\">old</span> friend"
    ),
    OrderedDict(
        title='Hypothesis',
        stack=[
            "Config",
            "[normalization]",
            "Lowercase"
        ],
        diff="<span class=\"delete\">H</span><span class=\"insert\">h</span>ello darkness my "
             "old foe"
    ),

    OrderedDict(
        title='Hypothesis',
        stack=[
            "Config",
            "[normalization]"
        ],
        diff="<span class=\"delete\">H</span><span class=\"insert\">h</span>ello darkness my "
             "old foe"
    ),
    OrderedDict(
        title='Hypothesis',
        stack=[
            "Config"
        ],
        diff="<span class=\"delete\">H</span><span class=\"insert\">h</span>ello darkness my "
             "old foe"
    ),
]


@pytest.fixture
def client():
    from benchmarkstt.api.cli import create_app
    app = create_app()
    client = app.test_client()
    yield client


def test_general_stuff(client):
    assert client.get('/').status_code == 404
    assert client.get('/api').status_code == 405
    assert client.post('/api').status_code == 400


@pytest.mark.parametrize('method,params,result', [
    ['version', {}, __version__],
    ['help', {}, None],
    ['list.normalization', {}, None],
    ['normalization.replace', {"text": "Nudge nudge!", "search": "nudge", "replace": "wink"}, {"text": 'Nudge wink!'}],
    ['metrics.diffcounts', {"ref": "Hello M", "hyp": "Hello W"}, {"equal": 1, "replace": 1, "insert": 0, "delete": 0}],
    ['benchmark.wer', benchmarkparams, {"wer": 0.2}],
    ['benchmark.diffcounts', benchmarkparams, {'diffcounts': {'delete': 0, 'equal': 4, 'insert': 0, 'replace': 1}}],
    ['benchmark.wer', dict(**benchmarkparams, return_logs="on"), dict(wer=0.2, logs=benchmarklogs)],
    ['benchmark.diffcounts', dict(**benchmarkparams, return_logs="on"),
     dict(diffcounts={'delete': 0, 'equal': 4, 'insert': 0, 'replace': 1}, logs=benchmarklogs)],
])
def test_correct_calls(method, params, result, client):
    request = {
      "jsonrpc": "2.0",
      "id": "6gpigblrn4",
      "params": params,
      "method": method
    }
    expected_response = {
        "jsonrpc": "2.0",
        "result": result,
        "id": "6gpigblrn4"
    }

    response = client.post('/api', data=json.dumps(request))
    assert response.status_code == 200

    if result is None:
        return

    if 'logs' in result:
        assert json.loads(response.data)['result']['logs'] == result['logs']

    assert json.loads(response.data) == expected_response


@pytest.mark.parametrize('method,params,code,result', [
    ['doesntexistmethod', {}, 404, {"code": -32601, "message": "Method not found", "data": "doesntexistmethod"}],
    ['normalization.config',
     {"text": "He bravely turned his tail and fled", "file": "/etc/hosts", "encoding": "UTF-8"},
     400,
     {
         "code": -32602,
         "message": "Invalid parameters",
         "data": "{\"message\": \"Access to unallowed file attempted\", \"field\": \"file\"}"
     }
     ],
])
def test_error_calls(method, params, code, result, client):
    request = {
        "jsonrpc": "2.0",
        "id": "6gpigblrn4",
        "params": params,
        "method": method
    }

    expected_response = {
        "jsonrpc": "2.0",
        "error": result,
        "id": "6gpigblrn4"
    }

    response = client.post('/api', data=json.dumps(request))
    if code is not None:
        assert response.status_code == code
    if result is not None:
        assert json.loads(response.data) == expected_response
