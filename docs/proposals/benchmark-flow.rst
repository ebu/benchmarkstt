===============================================
Handling multiple files for normalization rules
===============================================

-  Status: for discussion
-  Deciders: all
-  Date: 23/04/2019

---------------
Technical Story
---------------

Multiple files will be needed to be used, and combined, for creating a usable normalizer.
Throughout this document we will use the Command Line Interface (CLI) as an example, but these decisions *MAY* extend to eg. JSON-RPC API usage.

----------
References
----------

- `Add simple flow based on current normalizers and metrics #53 <https://github.com/ebu/ai-benchmarking-stt/issues/46>`_
- `Handling multiple files for normalization rules #46 <https://github.com/ebu/ai-benchmarking-stt/issues/53>`_

-----------------------------
Context and Problem Statement
-----------------------------

How can the user easily and in a non-confusing way provide multiple normalization files? What are the possible issues with each proposed solution?

----------------
Decision Drivers
----------------

(Also see: `Project Principles <https://github.com/ebu/ai-benchmarking-stt/wiki/Principles>`_)

- Usability: reduce complexity so the user can easily start using the toolkit without reading pages of documentation and avoiding user confusion due to non-intuitive program-specific rules
- Extensibility: the user still needs to be able to adapt rulesets

------------------
Considered Options
------------------

- Command line options
- Path-based rule files loading
- File-based rule files loading
- File-based rule loading
- Allow all/combination of the above

In the below examples we assume the current structure to be upheld:

.. code-block:: text

   benchmarkstt --reference ref.txt --hypothesis hyp.txt --metric wer --language en-GB

This provides a reference file, hypothesis file, a metric to calculate and a language, since these arguments are outside the scope of this proposal, in the below examples when `benchmarkstt` is used you can assume the above arguments are provided as well...

Also note that names such as 'pairs', 'regex', 'utf8decode', etc. are still up for discussion and used as examples only.

Command line options
--------------------

Provide all options through command line parameters.

Some examples:

.. code-block:: text

   benchmarkstt --lowercase --replace en-GB/numbers.csv
   benchmarkstt --replace file1.csv --replace file2.csv --replace file3.csv --regexreplace regex1.csv --regexreplace regex2.csv

Pros:

- Very verbose
- Very standardized and extensible

Cons:

- Extremely long command line statements would be commonplace
- Not easily readable
- Not very re-usable/easy to share

Path-based rule files loading
-----------------------------

Provide rule files in a single directory, apply them all.

Some examples:

.. code-block:: text

   benchmarkstt /tmp/myrulesfolder
   benchmarkstt en-GB/
   benchmarkstt nl_BE

The provided directory may have a structure such as this:

.. code-block:: text

   ./en-GB/regex_file_1
   ./en-GB/regex_file_2
   ./en-GB/pairs_file_1
   ./en-GB/pairs_file_2

Or, maybe:

.. code-block:: text

   ./en-GB/somefilename.regex
   ./en-GB/otherfilename.regex
   ./en-GB/numbers.pairs.csv
   ./en-GB/institutions.pairs.csv

The actual filenames are still up for discussion.

Pros:

- Simplicity

Cons:

- In what order files are processed?
- How do we recognize what type of normalizer is used for each file?
- What about normalizers that don't require a file of their own (eg. lowercase, utf-8 decode)?
- How do we support custom/non-standard normalizers?
- How would we re-use rules (symbolic links, do we need to copy files)?
- Difficult for prototyping/testing, would need to add, delete, rename files to change order or disable/enable.
- Do we process sub-folders? How?
- Do we follow symbolic links (shortcuts on windows)?

File-based rule files loading
-----------------------------

Much like "Path-based rule files loading", which solves a number of cons.

Some examples:

.. code-block:: text

   benchmarkstt en-GB.txt
   benchmarkstt myfilename

Where the file would contain file names, eg.

.. code-block:: text

   ~/en-GB.csv
   ~/all-languages/numbers.csv
   /tmp/any-location/any-file.csv

Pros:

- Still easy to use and understand
- These cons of path-based are resolved:

   * In what order files are processed? (This would just be top-to-bottom)
   * Difficult for prototyping/testing, would need to add, delete, rename files to change order or disable/enable.
   * Do we process sub-folders? How?
   * Do we follow symbolic links (shortcuts on windows)?
   * How would we re-use rules (symbolic links, do we need to copy files)?

Cons:

- How do we recognize what type of normalizer is used for each file?
- What about normalizers that don't require a file of their own (eg. lowercase, utf-8 decode)?
- How do we support custom/non-standard normalizers?

File-based rule loading
-----------------------

We provide a rules file describing the rules.

Examples:

.. code-block:: text

   benchmarkstt myrulesfile
   benchmarkstt en-GB.conf

A rules file describes a rule per line:

.. code-block:: text

   utf8decode
   pairs en-GB/numbers.csv

   regex en-GB/regex.csv

   regex all-languages/regexes.csv
   rules another-rulesfile.csv

   MyOwnCustomNormalizer
   # Some comment, eg. comment out a rule:
   # regex testing-regexes.csv

Pros:

- Still quite simple to use
- Very descriptive, even allowing comments and empty lines
- Easily used for prototyping/testing (easily change order of normalizers, comment one out, etc)
- Transparant order of normalizers (top-to-bottom)
- No amibiguity about which normalizer uses what input file as this is explicitly stated
- Support of non-filebased normalizers such as lowercase and utf8decode
- Support for non-standard/custom normalizers

Cons:

- Even though simple, it requires the user to understand that the normalizer needs to be explicitly stated (eg. ``regex regexfile``)

Allow all/combination of the above
----------------------------------

A combination of the above can be supported as well, this would just mean that the type of normalization should be specified.

We may want to limit that to only the "main" normalizers, i.e. no ``--lowercase``, etc. But only support eg. ``--path directory/``, ``--rules rulesfile``, ``--filelist fileslist.txt``. This would essentially exclude the first proposed option 'Command Line Arguments'.

Examples:

.. code-block:: text

   benchmarkstt --lowercase --path en-GB/ --regex all-languages/simpleregexes.csv
   benchmarkstt --filelist "list-of-files.txt" --rules rules.conf
   benchmarkstt --rules rules.conf
   benchmarkstt --path nl_BE
   benchmarkstt --rules rules.conf

Pros:

- Allows the user to decide which best fits his needs or preferences
- Much more verbose and descriptive
- All the pros of each proposed notation is essentially combined.

Cons:

- All the cons of each proposed notation is essentially combined.