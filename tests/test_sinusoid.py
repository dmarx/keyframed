from keyframed import SinusoidalCurve
import pytest
import math

EPS = 1e-9

def test_sine_simple():
    #c = SinusoidalCurve(frequency=1)
    c = SinusoidalCurve(wavelength=math.pi*2)
    assert abs(c[0] - 0) < EPS
    assert abs(c[math.pi] - 0) < EPS
    assert abs(c[2*math.pi] - 0) < EPS
    assert abs(c[math.pi/2] - 1) < EPS
    assert abs(c[3*math.pi/2] +1) < EPS