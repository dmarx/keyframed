from keyframed import Curve
import pytest
from loguru import logger

def test_simple_slicing():
    c0=Curve()
    assert c0 == c0[:]