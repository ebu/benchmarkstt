Subcommand api
==============

.. argparse::
   :module: conferatur.cli
   :func: _parser
   :prog: conferatur
   :path: api


An example POST request:

    .. code-block:: json

        {
            "jsonrpc": "2.0",
            "method": "normalisation",
            "params": {
                "text": "te TEST 𝔊𝔯𝔞𝔫𝔡𝔢 𝔖𝔞𝔰𝔰",
                "normalisers": [
                    ["replace", "te","test2"],
                    ["lowercase"],
                    ["unidecode"]
                ]
            },
            "id": null
        }

will return:

   .. code-block:: json

        {
            "jsonrpc": "2.0",
            "result": "test2 test Grande Sass",
            "id": null
        }
