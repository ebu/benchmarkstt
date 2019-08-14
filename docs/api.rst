API
===

BenchmarkSTT exposes its functionality through a JSON-RPC_ api.

.. attention::
   Only supported for Python versions 3.6 and above!

Starting the server
-------------------

You can launch a server to make the api available via:

    - :doc:`cli/api` (for debugging and local use only)
    - :doc:`docker`
    - gunicorn, by running ``gunicorn -b :8080 benchmarkstt.api.gunicorn``


Usage
-----

All requests must be HTTP POST requests, with the content containing valid JSON_.

Using curl, for example::

    curl -X POST \
      http://localhost:8080/api \
      -H 'Content-Type: application/json-rpc' \
      -d '{
        "jsonrpc": "2.0",
        "method": "help",
        "id": null
    }'

If you started the service with parameter ``--with-explorer`` (see :doc:`cli/api`), you can easily test the available JSON-RPC_
api calls by visiting the api url (eg. `http://localhost:8080/api` in the above example).

.. important::
   The API explorer is provided as-is, without any tests or code reviews. This
   is marked as a low-priority feature.

.. toctree::
   :maxdepth: 2

   api-methods


.. _JSON-RPC: https://www.jsonrpc.org
.. _JSON: http://www.json.org/



