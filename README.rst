Benchmarking STT
================

.. image:: https://img.shields.io/github/license/ebu/benchmarkstt.svg
    :target: https://github.com/ebu/benchmarkstt/blob/master/LICENCE.md

.. image:: https://img.shields.io/azure-devops/build/danielthepope/benchmarkstt/4/master.svg?logo=azure-devops
    :target: https://dev.azure.com/danielthepope/benchmarkstt/_build/latest?definitionId=4&branchName=master

.. image:: https://img.shields.io/azure-devops/tests/danielthepope/benchmarkstt/4/master.svg?logo=azure-devops
    :target: https://dev.azure.com/danielthepope/benchmarkstt/_build/latest?definitionId=4&branchName=master

.. image:: https://img.shields.io/azure-devops/coverage/danielthepope/benchmarkstt/4/master.svg?logo=azure-devops
    :target: https://dev.azure.com/danielthepope/benchmarkstt/_build

A tool for benchmarking Automatic Speech Recognition engines designed for non-academic production environments (see more below). 

Usage
-----

.. code-block:: bash

``$ benchmarkstt reference.txt hypothesis.txt --wer``
.....................................................
Return the Word Error Rate for an automatically generated transcript (hypothesis) by comparing it to the ground truth (referece).


.. code-block:: bash

``$ benchmarkstt reference.txt hypothesis.txt --wer --lowercase``
...................................................................
Return the Word Error Rate after lowercasing both reference and hypothesis. This improves the accuracy of the Word Error Rate.

.. code-block:: bash

``$ benchmarkstt reference.txt hypothesis.txt --worddiffs --wer --lowercase --config conf``
.............................................................................................
Return WER and a visual diff after applying all the normalization rules specified in the config file.




This is a collaborative project to create a library for benchmarking AI/ML applications. It evolved out of conversations among broadcasters and providers of Access Services to media organisations, but anyone is welcome to contribute. The group behind this project is the EBU's `Media Information Management & AI group <https://tech.ebu.ch/groups/mim>`_. Currently the group is focussing on Speech-to-Text, but it will consider creating benchmarking tools for other AI/ML services.

For general information about this project, including the `motivations <https://github.com/ebu/benchmarkstt/wiki>`_ and `guiding principles <https://github.com/ebu/benchmarkstt/wiki/Principles>`_, please see the project `wiki <https://github.com/ebu/benchmarkstt/wiki>`_ and `documentation <https://ebu.github.io/benchmarkstt/>`_.


