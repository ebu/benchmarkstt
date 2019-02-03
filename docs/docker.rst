Running as a docker image
=========================

Build the image
---------------

Inside the conferatur folder (see :doc:`INSTALL`) run:

   .. code-block:: bash

      docker build -t conferatur:latest .


Run the image
-------------

You can change port for the api, just change the :code:`8000` to the port you want to bind to.

   .. code-block:: bash

      docker run --name conferatur -p 8000:5000 --rm conferatur:latest

The jsonrpc api is then automatically available at: :code:`http://localhost:8000/api`

While the docker image is running you can use the CLI application like this (see :doc:`usage` for
more information about which commands are available):

   .. code-block:: bash

      docker exec -it conferatur conferatur --version
      conferatur --help


Stopping the image
------------------

You can stop the docker image running by:

   .. code-block:: bash

      docker stop conferatur
