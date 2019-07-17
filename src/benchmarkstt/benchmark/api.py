import benchmarkstt.metrics as metrics
from io import StringIO
from benchmarkstt.input.core import PlainText
from benchmarkstt.normalization.core import Config
from benchmarkstt.normalization.logger import LogCapturer

factory = metrics.factory


def callback(cls, ref: str, hyp: str, config: str = None, return_logs: bool = None, *args, **kwargs):
    """
    :param ref: Reference text
    :param hyp: Hypothesis text
    :param config: The config to use
    :param bool return_logs: Return normalization logs

    :example ref: 'Hello darkness my OLD friend'
    :example hyp: 'Hello darkness my old foe'
    :example config:

            .. code-block:: text

                [normalization]
                # using a simple config file
                Lowercase

    :example result: ""
    """

    normalizer = None
    if config is not None and len(config.strip()):
        normalizer = Config(StringIO(config), section='normalization')

    ref = PlainText(ref, normalizer=normalizer)
    hyp = PlainText(hyp, normalizer=normalizer)

    metric = cls(*args, **kwargs)
    cls_name = cls.__name__.lower()

    if not return_logs:
        result = metric.compare(list(ref), list(hyp))
        if isinstance(result, tuple) and hasattr(result, '_asdict'):
            result = result._asdict()
        return {
            cls_name: result
        }

    with LogCapturer(dialect='html', diff_formatter_dialect='dict', title='Reference') as logcap:
        ref = list(ref)
        logs_ref = logcap.logs

    with LogCapturer(dialect='html', diff_formatter_dialect='dict', title='Hypothesis') as logcap:
        hyp = list(hyp)
        logs_hyp = logcap.logs

    result = metric.compare(ref, hyp)
    if isinstance(result, tuple) and hasattr(result, '_asdict'):
        result = result._asdict()

    return {
        cls_name: result,
        "logs": logs_ref + logs_hyp
    }
