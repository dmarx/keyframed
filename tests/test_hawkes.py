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

    assert c.to_dict(simplify=True) == {'parameters': {1: {'curve': {0: {'value': 0, 'interpolation_method': 'exp_decay', 'interpolator_arguments': {'decay_rate': 0.5}}, 1: {'value': 1}}}}, 'reduction': 'sum'}
    
    c.add_event(3)
    assert c.to_dict(simplify=True) == {'parameters': {1: {'curve': {0: {'value': 0, 'interpolation_method': 'exp_decay', 'interpolator_arguments': {'decay_rate': 0.5}}, 1: {'value': 1}}}, 3: {'curve': {0: {'value': 0, 'interpolation_method': 'exp_decay', 'interpolator_arguments': {'decay_rate': 0.5}}, 3: {'value': 1}}}}, 'reduction': 'sum'}