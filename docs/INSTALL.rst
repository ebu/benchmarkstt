Installation
============

BenchmarkSTT requires Python_ version 3.5 or above.


From PyPI (preferred)
---------------------

This is the easiest and preferred way of installing benchmarkstt.

TODO


From source
-----------

1. Install Python_ 3.5 or above (latest stable version for your OS is preferred):

   Use the guides available at `The Hitchhiker’s Guide to Python <https://docs.python-guide.org>`_

    - `Installing Python 3 on Mac OS X <https://docs.python-guide.org/starting/install3/osx/>`_
    - `Installing Python 3 on Windows <https://docs.python-guide.org/starting/install3/win/>`_
    - `Installing Python 3 on Linux <https://docs.python-guide.org/starting/install3/linux/>`_

2. Install the package using :code:`pip`, this will also install all requirements

   .. code-block:: bash

      pip install https://github.com/ebu/benchmarkstt/archive/master.zip

3. Test and use

   BenchmarkSTT should now be installed and usable.

   .. parsed-literal::

      $ benchmarkstt --version
      benchmarkstt: |version|
      $ echo IT WORKS! | benchmarkstt-tools normalization --lowercase
      it works!


   Use the :code:`--help` option to get all available options.

   .. code-block:: bash

      benchmarkstt --help
      benchmarkstt-tools normalization --help

   See :doc:`usage` for more information on how to use.


Removing benchmarkstt
---------------------

   .. code-block:: bash

      pip uninstall benchmarkstt


Docker
------

See instructions for setting up and running as a docker_ image at:

    .. toctree::
       :maxdepth: 2

       docker


.. _Python: https://www.python.org
.. _docker: https://www.docker.com
