from benchmarkstt.input.core import PlainText
import benchmarkstt.metrics as metrics

factory = metrics.factory


def callback(cls, ref: str, hyp: str, *args, **kwargs):
    try:
        ref = PlainText(ref)
        hyp = PlainText(hyp)
        return cls(*args, **kwargs).compare(ref, hyp)
    except Exception as e:
        raise Exception(e)


extra_params = [
    dict(name='ref', annotation=str, description='Reference'),
    dict(name='hyp', annotation=str, description='Hypothesis'),
]

