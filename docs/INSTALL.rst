Installation
============

BenchmarkSTT requires Python_ version 3.5 or above. If you wish to make use of the :doc:`api`, Python_ version 3.6 or
above is required.


From PyPI (preferred)
---------------------

This is the easiest and preferred way of installing ``benchmarkstt``.

1. Install Python_ 3.5 or above (latest stable version for your OS is preferred):

   Use the guides available at `The Hitchhiker’s Guide to Python <https://docs.python-guide.org>`_

    - `Installing Python 3 on Mac OS X <https://docs.python-guide.org/starting/install3/osx/>`_
    - `Installing Python 3 on Windows <https://docs.python-guide.org/starting/install3/win/>`_
    - `Installing Python 3 on Linux <https://docs.python-guide.org/starting/install3/linux/>`_

2. Install the package using ``pip``, this will also install all requirements::

      python3 -m pip install benchmarkstt

3. Test and use

   BenchmarkSTT should now be installed and usable.

   .. container:: terminal

      | $> benchmarkstt --version
      | benchmarkstt: |release|
      | $> echo IT WORKS! | benchmarkstt-tools normalization --lowercase
      | it works!


   Use the ``--help`` option to get all available options::

      benchmarkstt --help
      benchmarkstt-tools normalization --help

   See :doc:`usage` for more information on how to use.


Removing benchmarkstt
---------------------

BenchmarkSTT can be easily uninstalled using::

      python3 -m pip uninstall benchmarkstt


Docker
------

See instructions for setting up and running as a docker_ image at:

    .. toctree::
       :maxdepth: 2

       docker


.. _Python: https://www.python.org
.. _docker: https://www.docker.com
