"""
.. code-block:: none

    usage: normalisation [--help|-h] [--input-file|-i FILE] [--output-file|-o FILE]
                         --normaliser-name [argument ...]
                         [--normaliser-name [argument ...] ...]

    positional arguments:
      -h, --help              show this help message and exit

    optional arguments:
      You can provide multiple input and output files, each preceded by -i and -o
      respectively.
      If no input file is given, only one output file can be used.
      If using both multiple input and output files there should be an equal amount
      of each. Each processed input file will then be written to the corresponding
      output file.

      -i, --input-file FILE   read input from FILE, by default will use stdin
      -o, --output-file FILE  write output to FILE, by default will use stdout

      !!! WARNING: OUTPUT FILES ARE OVERWRITTEN IF THEY ALREADY EXIST !!!

    normalisers:
      A list of normalisers to execute on the input, can be one or more normalisers
      which are applied sequentially.
      The program will automatically find the normaliser in confertur.normalisers.core,
      then conferatur.normalisers and finally in the global namespace.
      At least one normaliser needs to be provided.

      --normaliser-name [arguments ...]
                               the name of the normaliser (eg. --lowercase),
                               optionally followed by arguments passed to the
                               normaliser
"""

import sys
from .core import CommandLineArguments


def main(args=None):
    # not using argparse for this one
    if '--help' in args or '-h' in args:
        helptext = __doc__.split('usage: ', 1)[1].replace("\n    ", "\n")
        print('usage: ' + helptext)
        exit()

    def err(txt, code=1):
        sys.stderr.write(txt + " Use `--help` for more information.\n")
        exit(code)

    def get_args(args, arg_names):
        if len(args) == 0:
            return None
        input_files_idx = [idx for idx, v in enumerate(args) if v in arg_names]
        if not len(input_files_idx):
            return None
        result = [args[idx + 1] for idx in input_files_idx]
        # delete from args list
        for idx in reversed(input_files_idx):
            del args[idx + 1]
            del args[idx]
        return result

    input_files = get_args(args, ('-i', '--input-file'))
    output_files = get_args(args, ('-o', '--output-file'))

    if len(args) == 0:
        err("Need at least one normaliser.")

    if not args[0].startswith('--'):
        err("Invalid argument '%s'." % (args[0]))

    if input_files is None and output_files is not None and len(output_files) > 1:
        err("Can only write output to one file when reading from stdin.")
    elif input_files is not None and output_files is not None:
        # straight mapping from input to output, needs equal length
        if len(input_files) != len(output_files):
            err("When using multiple input or output files, there needs to be an equal amount of each.")

    normaliser = CommandLineArguments(args)

    if input_files is not None:
        for idx, file in enumerate(input_files):
            with open(file) as input_file:
                text = input_file.read()
            text = normaliser.normalise(text)
            if output_files is None:
                sys.stdout.write(text)
            else:
                with open(output_files[idx]) as output_file:
                    output_file.write(text)
    else:
        text = sys.stdin.read()
        text = normaliser.normalise(text)
        if output_files is None:
            sys.stdout.write(text)
        else:
            with open(output_files[0], 'w') as output_file:
                output_file.write(text)


if __name__ == '__main__':
    main(sys.argv[1:])
