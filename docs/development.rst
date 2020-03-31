Development
===========

Setting up environment
----------------------

This assumes ``git`` and ``Python`` 3.5 or above are already installed on your system (see :doc:`INSTALL`).

1. Fork the `repository source code <https://github.com/EBU/benchmarkstt.git>`_ from github to your own account.

2. Clone the repository from github to your local development environment (replace ``[YOURUSERNAME]`` with your
   github username)::

      git clone https://github.com/[YOURUSERNAME]/benchmarkstt.git
      cd benchmarkstt

3. Create and activate a local environment::

      python3 -m pip install venv
      python3 -m venv env
      source env/bin/activate

4. Install the package, this will also install all requirements. This does an "editable" install, i.e.
   it creates a symbolic link to the source code::

      make dev

5. You now have a local development environment where you can commit and push to your own forked repository. It is recommended to run the tests to check your local copy passes all unit tests::

      make test

.. warning::

   The development version of ``benchmarkstt`` and ``benchmarkstt-tools`` is only available in your current `venv` environment. Make sure to run ``source env/bin/activate`` to activate your local `venv` before making calls to ``benchmarkstt`` or ``benchmarkstt-tools``.


Building the documentation
--------------------------

First install the dependencies for building the documentation (sphinx, etc.) using::

      make setupdocs

This only needs to be done once.

Then to build the documentation locally::

      make docs

The documentation will be created in /docs/build/html/


Contributing
------------

.. toctree::
   :maxdepth: 1

   CONTRIBUTING
   CODE_OF_CONDUCT

