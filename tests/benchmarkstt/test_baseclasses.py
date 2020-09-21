from benchmarkstt.normalization import Normalizer as NormalizationBase
from benchmarkstt.metrics import Metric as MetricsBase
from benchmarkstt.diff import Differ as DiffBase
from benchmarkstt.segmentation import Segmenter as SegmentationBase
from benchmarkstt.input import Input as InputBase
import pytest
from inspect import signature


@pytest.mark.parametrize('base_class,methods', [
    [NormalizationBase, '_normalize'],
    [MetricsBase, 'compare'],
    [DiffBase, ['__init__', 'get_opcodes']],
    [SegmentationBase, '__iter__'],
    [InputBase, '__iter__'],
])
def test_baseclasses(base_class, methods):
    if type(methods) is str:
        methods = [methods]
    for method in methods:
        to_call = getattr(base_class, method)
        sig = signature(to_call)
        with pytest.raises(NotImplementedError):
            args = [None] * len(sig.parameters)
            to_call(*args)
