============
Architecture
============

Modules
-------

BenchmarkSTT contains a couple of submodules that interconnect to provide benchmarking functionality.

These are:

input
  Provides ways of dealing with input formats and converting them to benchmarkstt native schema

normalization
  Provides a number of methods of normalizing text

diff
  Provides a matching algorithm

segmentation
  Provides ways of segmenting input

output
  Provides ways to output results


Usage by `benchmarkstt`
-----------------------

.. uml::

  actor User

  User -> benchmarkstt

  benchmarkstt -> input
  input -> segmentation
  segmentation -> TODO

