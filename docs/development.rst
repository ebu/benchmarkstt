Development
===========

Setting up environment
----------------------

This assumes :code:`git` and :code:`Python` 3.5 or above are already installed on your system (see :doc:`INSTALL`).

1. Fork the `repository source code <https://github.com/EBU/benchmarkstt.git>`_ from github to your own account.

2. Clone the repository from github to your local development environment (replace :code:`[YOURUSERNAME]` with your
   github username).

   .. code-block:: bash

      git clone https://github.com/[YOURUSERNAME]/benchmarkstt.git
      cd benchmarkstt

3. Install the package using :code:`pip`, this will also install all requirements. This does an "editable" install, i.e.
   it creates a symbolic link to the source code.

   .. code-block:: bash

      pip install -e .

4. You now have a local development environment where you can commit and push to your own forked repository.


Building the documentation
--------------------------

Build the documentation locally:

   .. code-block:: bash

      pip install -r docs/requirements.txt
      make docs

The documentation will be created in /docs/build/html/




Contributing
------------

.. toctree::
   :maxdepth: 1

   CONTRIBUTING
   CODE_OF_CONDUCT

