Command line tool
=================

    .. argparse::
       :module: benchmarkstt.cli.main
       :func: argparser
       :prog: benchmarkstt

Implementation
--------------

The `benchmarkstt` command line tool links the different modules (`input`, `normalization`, `metrics`, etc.) in the following way:

    .. image:: img/benchmarkstt.cli.svg
        :alt: CLI flow


Additional tools
----------------

Some additional helpful tools are available through ``benchmarkstt-tools``, which provides these subcommands:

   .. toctree::
      :maxdepth: 1

      cli/api
      cli/normalization
      cli/metrics

Bash completion
---------------

Bash completion is supported through ``argcomplete``.

    .. toctree::

       bash-completion

.. _JSON-RPC: https://www.jsonrpc.org
