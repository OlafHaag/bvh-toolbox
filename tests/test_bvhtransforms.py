import collections

from hypothesis import given
from hypothesis import example
from hypothesis import assume
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays
import pytest
import numpy as np
import bvhtoolbox as bt


@given(a=arrays(dtype=np.float,
                shape=st.tuples(st.integers(min_value=0, max_value=600),
                                st.integers(min_value=0, max_value=100)),
                elements=st.floats(allow_nan=False)),
       epsilon=st.floats())
def test_prune(a, epsilon):
    assume(not np.isnan(epsilon))
    bt.prune(a, epsilon)
    assert np.all((a == 0.0) | (epsilon <= np.abs(a)))


@given(order=st.text().filter(lambda x: x not in bt._AXES2TUPLE.keys()))
def test_get_reordered_indices_invalid_input(order):
    with pytest.raises(KeyError):
        res = bt._get_reordered_indices(order)


@given(order=st.sampled_from(list(bt._AXES2TUPLE.keys())))
def test_get_reordered_indices(order):
    res = bt._get_reordered_indices(order)
    assert isinstance(res, collections.Iterable)
    assert sorted(res) == [0, 1, 2]
    
    
@given(a=arrays(dtype=np.float,
                shape=tuple(np.random.randint(1, 5) for _ in range(np.random.randint(1, 4))),
                elements=st.floats(allow_nan=False)),
       axes=st.sampled_from(list(bt._AXES2TUPLE.keys())))
def test_reorder_axes_invalid_dimensionality(a, axes):
    with pytest.raises(NotImplementedError):
        bt.reorder_axes(a, axes=axes)


# @given(a=arrays(dtype=np.float,
#                 shape=st.one_of(st.just(3),st.tuples(st.integers(min_value=1), st.just(3))),
#                 elements=st.floats(allow_nan=False, allow_infinity=False),
#                 unique=True),
#        axes=st.sampled_from(list(bt._AXES2TUPLE.keys())))
@given(axes=st.sampled_from(list(bt._AXES2TUPLE.keys())))
@example(a=np.random.random((10, 3)))
@example(a=np.random.random(3))
def test_reorder_axes(a, axes):
    res = bt.reorder_axes(a, axes=axes)
    assert isinstance(res, np.ndarray)
# Todo: output for axes='xyz' should match xyz input.
# Todo: output should be reordered.


if __name__ == '__main__':
    test_prune()
    test_get_reordered_indices_invalid_input()
    test_get_reordered_indices()
