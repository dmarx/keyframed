from keyframed import Curve
import pytest
from loguru import logger

EPS = 1e-9

def test_simple_slicing():
    c0=Curve()
    assert c0 == c0[:]

def test_interpolated_slicing_left():
    c0=Curve({10:10}, default_interpolation='linear')
    c1 = c0[:5]
    for i in range(6):
        #assert c0[i] == c1[i]
        assert abs(c0[i] - c1[i]) < EPS
    assert c1[6] == 5

def test_interpolated_slicing_right():
    c0=Curve({10:10}, default_interpolation='linear')
    k = 5
    c1 = c0[k:]
    print(c1._data)
    for i in range(10):
        j = i-k
        if j < 0:
            continue
        assert c0[i] == c1[j]
