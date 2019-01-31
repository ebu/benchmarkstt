Setting up bash completion
==========================

If you use ``bash`` as your shell, ``conferatur`` can use `argcomplete <https://argcomplete.readthedocs.io>`_ for auto-completion.

For this ``argcomplete`` needs to be installed **and** enabled.

First install argcomplete using:

   .. code-block:: bash

      pip install argcomplete

For global activation of all argcomplete enabled python applications, run:

   .. code-block:: bash

      sudo activate-global-python-argcomplete

For permanent (but not global) ``conferatur`` activation, use:

   .. code-block:: bash

      register-python-argcomplete conferatur >> ~/.bashrc

For one-time activation of argcomplete for ``conferatur`` only, use:

   .. code-block:: bash

      eval "$(register-python-argcomplete conferatur)"

