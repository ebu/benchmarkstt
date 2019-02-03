API
===

Conferatur exposes its functionality through a JSON-RPC_ api.

Starting the server
-------------------

You can launch a server to make the api available via:

    - :doc:`cli/api` (for debugging and local use only)
    - :doc:`docker`
    - gunicorn, by running :code:`start_gunicorn.sh` in the root repository folder


Usage
-----

All requests must be HTTP POST requests, with the content containing valid JSON_.

Using curl, for example:

.. code-block:: none

    curl -X POST \
      http://localhost:5000/ \
      -H 'Content-Type: application/json-rpc' \
      -d '{
        "jsonrpc": "2.0",
        "method": "help",
        "id": null
    }'


.. toctree::
   :maxdepth: 2

   api-methods


.. _JSON-RPC: https://www.jsonrpc.org
.. _JSON: http://www.json.org/



