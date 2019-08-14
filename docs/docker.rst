Using docker
============

.. warning::

   This assumes docker_ is already installed on your system.

Build the image
---------------

1. Download the code from github at https://github.com/ebu/benchmarkstt/archive/master.zip

2. Unzip the file

3. Inside the benchmarkstt folder run::

      docker build -t benchmarkstt:latest .

Run the image
-------------

You can change port for the api, just change the ``1234`` to the port you want to bind to::

      docker run --name benchmarkstt -p 1234:8080 --rm benchmarkstt:latest

The json-rpc api is then automatically available at: ``http://localhost:1234/api``

While the docker image is running you can use the CLI application like this (see :doc:`usage` for
more information about which commands are available)::

      docker exec -it benchmarkstt benchmarkstt --version
      docker exec -it benchmarkstt benchmarkstt --help
      docker exec -it benchmarkstt benchmarkstt-tools --help


Stopping the image
------------------

You can stop the docker image running by running::

      docker stop benchmarkstt


.. _docker: https://www.docker.com