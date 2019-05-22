import pytest
import json

from benchmarkstt.__meta__ import __version__
from benchmarkstt.api.cli import create_app


@pytest.fixture
def client():
    app = create_app()
    client = app.test_client()
    yield client


def test_general_stuff(client):
    assert client.get('/').status_code == 404
    assert client.get('/api').status_code == 405
    assert client.post('/api').status_code == 400


@pytest.mark.parametrize('method,params,result', [
    ['version', {}, __version__],
])
def test_correct_calls(method, params, result, client):
    request = {
      "jsonrpc": "2.0",
      "id": "6gpigblrn4",
      "params": params,
      "method": method
    }
    response = {
        "jsonrpc": "2.0",
        "result": result,
        "id": "6gpigblrn4"
    }
    assert json.loads(client.post('/api', data=json.dumps(request)).data) == response
