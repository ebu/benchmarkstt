Installation
============

Conferatur requires Python_ version 3.4 or above.

From PyPI (preferred)
---------------------

This is the easiest and preferred way of installing conferatur.

TODO


From source
-----------

1. Install Python_ 3.3 or above (latest stable version for your OS is preferred):

   Use the guides available at `The Hitchhiker’s Guide to Python <https://docs.python-guide.org>`_

    - `Installing Python 3 on Mac OS X <https://docs.python-guide.org/starting/install3/osx/>`_
    - `Installing Python 3 on Windows <https://docs.python-guide.org/starting/install3/win/>`_
    - `Installing Python 3 on Linux <https://docs.python-guide.org/starting/install3/linux/>`_

2. Get the conferatur source code from github (assumes :code:`git` is installed on the system)

   .. git clone https://github.com/ebu/ai-benchmarking-stt.git

   .. code-block:: bash

      git clone https://github.com/MikeSmithEU/ai-benchmarking-stt.git

3. Install the package using :code:`pip`, this will also install all requirements

   .. code-block:: bash

      pip install ai-benchmarking-stt

   Once this is done you may remove the git repository (optional).

   .. code-block:: bash

      rm -fr ai-benchmarking-stt

4. Test and use

   Conferatur should now be installed and usable.

   .. code-block:: none

      $ echo "IT WORKS" | conferatur normalisation --lowercase
      it works


   Use the :code:`--help` option to get all available options.

   .. code-block:: bash

      conferatur --help
      conferatur normalisation --help

Removing conferatur
-------------------

   .. code-block:: bash

      pip uninstall conferatur

.. _Python: https://www.python.org
