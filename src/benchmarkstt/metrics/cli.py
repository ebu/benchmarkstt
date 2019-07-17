"""
Calculate metrics based on the comparison of a hypothesis with a reference.
"""

from benchmarkstt.input import core
from benchmarkstt.output import factory as output_factory
from benchmarkstt.metrics import factory
from benchmarkstt.cli import args_from_factory
from benchmarkstt.normalization.logger import Logger
import argparse
from inspect import signature, Parameter
import logging
from collections import OrderedDict


def argparser(parser: argparse.ArgumentParser):
    # steps: input normalize[pre?] segmentation normalize[post?] compare

    parser.add_argument('-r', '--reference', help='File to use as reference', required=True)
    parser.add_argument('-h', '--hypothesis', help='File to use as hypothesis', required=True)

    types = OrderedDict(infer=' '.join([core.File.__doc__.strip(),
                                        'Automatically infer file type from the filename extension.']),
                        argument='Read the argument and treat as plain text (without reading from file)',
                        **core.File.available_types())
    types_help = ['Available types:']
    types_help.extend(['%r: %s' % (k, v) for k, v in types.items()])
    types_help = '\n'.join(types_help)

    subparser = parser.add_argument_group('reference and hypothesis types',
                                          description='You can specify which file type the --reference/-r and ' +
                                                      '--hypothesis/-h arguments should be treated as.\n\n' +
                                                      types_help)

    subparser.add_argument('-rt', '--reference-type', default='infer',
                           help='Type of reference file', choices=types.keys())
    subparser.add_argument('-ht', '--hypothesis-type', default='infer',
                           help='Type of hypothesis file', choices=types.keys())

    parser.add_argument('-o', '--output-format', default='restructuredtext', choices=output_factory.keys(),
                        help='Format of the outputted results')

    metrics_desc = "A list of metrics to calculate. At least one metric needs to be provided."

    subparser = parser.add_argument_group('available metrics', description=metrics_desc)
    args_from_factory('metrics', factory, subparser)
    return parser


def file_to_iterable(file, type_, normalizer=None):
    if type_ == 'argument':
        return core.PlainText(file, normalizer=normalizer)
    return core.File(file, type_, normalizer=normalizer)


def main(parser, args, normalizer=None):
    logging.getLogger()
    prev_title = Logger.title
    Logger.title = 'Reference'
    ref = list(file_to_iterable(args.reference, args.reference_type, normalizer=normalizer))
    Logger.title = 'Hypothesis'
    hyp = list(file_to_iterable(args.hypothesis, args.hypothesis_type, normalizer=normalizer))
    Logger.title = prev_title

    if 'metrics' not in args or not len(args.metrics):
        parser.error("need at least one metric")

    with output_factory.create(args.output_format) as out:
        for item in args.metrics:
            metric_name = item.pop(0).replace('-', '.')
            cls = factory[metric_name]
            kwargs = dict()

            # somewhat hacky default diff formats for metrics
            sig = signature(cls.__init__).parameters
            sigkeys = list(sig)

            if 'dialect' in sigkeys:
                idx = sigkeys.index('dialect') - 1
                sig = sig['dialect']
                if sig.kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.POSITIONAL_ONLY):
                    if len(item) <= idx:
                        if args.output_format == 'json':
                            kwargs['dialect'] = 'list'
                            if 'diff_formatter_dialect' in sigkeys:
                                kwargs['diff_formatter_dialect'] = 'dict'
                        else:
                            kwargs['dialect'] = 'cli'

            metric = cls(*item, **kwargs)
            result = metric.compare(ref, hyp)
            out.result(metric_name, result)
