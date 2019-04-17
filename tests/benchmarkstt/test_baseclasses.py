from benchmarkstt.normalization import Base as NormalizationBase
from benchmarkstt.metrics import Base as MetricsBase
from benchmarkstt.diff import Base as DiffBase
from benchmarkstt.segmentation import Base as SegmentationBase
from benchmarkstt.input import Base as InputBase
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
