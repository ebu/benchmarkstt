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

   .. code-block:: bash

      git clone https://github.com/ebu/ai-benchmarking-stt.git
      cd ai-benchmarking-stt

3. Install the package using :code:`pip`, this will also install all requirements

   .. code-block:: bash

      pip install .

   Once this is done you may remove the git repository.

   .. code-block:: bash

      cd .. && rm -fr ai-benchmarking-stt

4. Test and use

   Conferatur should now be installed and usable.

   .. code-block:: none

      $ echo "IT WORKS" | conferatur normalisation --lowercase
      it works


   Use the :code:`--help` option to get all available options.

   .. code-block:: bash

      conferatur --help
      conferatur normalisation --help

Development
-----------

For development you can run :code:`python conferatur/cli.py` (when inside the repository directory) instead of :code:`conferatur` to test the command line scripts.

Alternatively (on unix-based systems like Mac OS X and Linux) you can define an alias (again when inside the repository directory):

   .. code-block:: bash

      alias conferatur="python3 `pwd`/conferatur/cli.py"


The :code:`conferatur` command will then use your local source environment to run conferatur (for the current shell session).

To find out which conferatur script is being used in the current shell use :code:`type conferatur`.

.. code-block:: none

    $ type conferatur
    conferatur is /usr/local/bin/conferatur
    $ pwd
    /my/dev/dir/ai-benchmarking-stt
    $ alias conferatur="python3 `pwd`/conferatur/cli.py"
    $ type conferatur
    conferatur is aliased to `python3 /my/dev/dir/ai-benchmarking-stt/conferatur/cli.py'
    $ unalias conferatur
    $ type conferatur
    conferatur is /usr/local/bin/conferatur

Removing conferatur
-------------------

   .. code-block:: bash

      pip uninstall conferatur

.. _Python: https://www.python.org
