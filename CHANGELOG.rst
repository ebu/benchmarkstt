Changelog
=========

[Unreleased]
------------

Added
^^^^^


* 
  Documentation:


  * add auto-generated UML diagrams
  * add tutorial Jupyter Notebooks
  * add support for loading external/local code (`--load`) #142

* 
  Tests:


  * add python 3.8 to github workflow, re-enable excluded python versions

Changed
^^^^^^^


* 
  Cleanup/refactors:


  * group cli and api entrypoints in their respective packages
  * moved all documentation specific code outside main package
  * update sphinx to latest
  * use more descriptive names for Base classes (Normalizer, Differ, etc.)
  * rename CLIDiffDialect to ANSIDiffDialect, "cli" -> "ansi"
  * rename NormalizationComposite -> NormalizationAggregate
  * allow ducktyped custom classes to be recognized as valid
  * proper abstract base classes
  * move csv functionality to it's own repository "csvlike", add to requirements

* 
  Documentation:


  * custom autodoc templates

* Normalizer Unidecode and dependency 'Unidecode>=1.1.0' replaced by version working for python3.9

Fixed
^^^^^


* 
  Makefile: 


  * ensure pip is installed (in some cases needed for development, avoids user confusion)
  * use environment python if available, otherwise use python3

* 
  Dockerfile:


  * fixed missing python package by specifying its version #138

1.0.0 - 2020-04-23
------------------

Initial version
