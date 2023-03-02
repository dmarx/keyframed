import pytest
from loguru import logger
from keyframed import Curve

def test_append_curves():
    c0 = Curve({1:1, 2:2})
    c1 = c0.append(c0)
    print(c1)
    for i in range(3):
        print(i)
        assert c1[i] == c0[i]
        assert c1[i+3] == c0[i]
