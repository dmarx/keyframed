from keyframed import HawkesProcessIntensity
import pytest
import math

EPS = 1e-9

def test_hawkes_simple():
    c = HawkesProcessIntensity()
    with pytest.raises(ValueError):
        assert c[1] == 0 # empty hawkes process makes the thing angry
    c.add_event(1)
    assert c[1] == 1
    assert c[0] == 0
    assert c[0.5] == 0
    assert abs(c[2] - 0.951229424500714) < EPS
    
    c = HawkesProcessIntensity(decay=.5)
    c.add_event(1)
    assert c[1] == 1
    assert c[0] == 0
    assert c[0.5] == 0
    assert abs(c[2] - 0.6065306597126334) < EPS
