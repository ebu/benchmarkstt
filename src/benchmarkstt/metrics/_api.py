from benchmarkstt.input.core import PlainText
import benchmarkstt.metrics as metrics

factory = metrics.factory


def callback(cls, ref: str, hyp: str, *args, **kwargs):
    """
    :param ref: Reference text
    :param hyp: Hypothesis text
    """
    ref = PlainText(ref)
    hyp = PlainText(hyp)
    return cls(*args, **kwargs).compare(ref, hyp)
