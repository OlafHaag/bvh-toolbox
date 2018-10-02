from hypothesis import given
from hypothesis import assume
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays
import numpy as np

from bvhtransforms import *


@given(a=arrays(dtype=np.float,
                shape=st.tuples(st.integers(min_value=0, max_value=600),
                                st.integers(min_value=0, max_value=100)),
                elements=st.floats(allow_nan=False)),
       epsilon=st.floats())
def test_prune(a, epsilon):
    assume(not np.isnan(epsilon))
    prune(a, epsilon)
    assert np.all((a == 0.0) | (epsilon <= np.abs(a)))


if __name__ == '__main__':
    test_prune()
