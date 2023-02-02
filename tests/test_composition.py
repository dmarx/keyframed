from keyframed import ParameterGroup, Curve, SmoothCurve, Composition
import numpy as np
import math
from numbers import Number


EPS = 1e-9

def test_composition_direct():

    kfs = {0:0,1:1,10:10}
    pg = ParameterGroup({
        'stepfunc':Curve(kfs),
        'smoothfunc':SmoothCurve(kfs),
        'longstep':Curve({0:1, 15:15}),
    })

    additive = Composition(parameters=pg, reduction='add')
    multiplicative =  Composition(parameters=pg, reduction='multiply')
    
    assert abs(additive[4] - 5.25) < EPS
    assert abs(multiplicative[4] - 3.25) < EPS


def test_add_curves():
    c1 = Curve({1:1}, default_interpolation='linear')
    c2 = Curve({1:1})
    c3 = c1+c2
    assert isinstance(c3, Composition)
    for i in range(10):
        assert (c1[i] + c2[i]) == c3[i]
        assert (c2[i] + c1[i]) == c3[i]
    # test that c3 references original objects
    c1[1]=2
    for i in range(10):
        assert (c1[i] + c2[i]) == c3[i]
        assert (c2[i] + c1[i]) == c3[i]


def test_add_loop_to_curve():
    pass

def test_add_loop_to_loop():
    pass


def test_mul_curves():
    c1 = Curve({1:1}, default_interpolation='linear')
    c2 = Curve({1:2}, default_interpolation='linear')
    c3 = c1*c2
    assert isinstance(c3, Composition)
    for i in range(10):
        assert (c1[i] * c2[i]) == c3[i]
        assert (c2[i] * c1[i]) == c3[i]
    # test that c3 references original objects
    c1[1]=3
    for i in range(10):
        assert (c1[i] * c2[i]) == c3[i]
        assert (c2[i] * c1[i]) == c3[i]

def test_mul_curves2():
    cos_curve = Curve({0:0}, default_interpolation=lambda k,curve: math.cos(k))
    sin_curve = Curve({0:0}, default_interpolation=lambda k,curve: math.sin(k))

    xs = np.linspace(0,4*np.pi, 100)
    ys_cos = [cos_curve[x] for x in xs]
    ys_sin = [sin_curve[x] for x in xs]

    mul_curve = cos_curve * sin_curve
    ys_mul = [mul_curve[x] for x in xs]
    assert isinstance(ys_mul[0], Number)

def test_mul_loop_to_curve():
    pass

def test_mul_loop_to_loop():
    pass


def test_add_loop_to_pg():
    pass

def test_mul_loop_to_pg():
    pass

def test_add_comp_to_comp():
    pass

def test_mul_comp_to_comp():
    pass


def test_composition_of_composition():
    c1 = Curve({1:1}, default_interpolation='linear')
    c2 = Curve({1:1})
    c3 = c1+c2
    c4 = c3 * c1
    for i in range(10):
        assert c4[i] == (c1[i] + c2[i]) * c1[i]

def test_float_arithmetic_on_nested_composition():
    c1 = Curve({1:1}, default_interpolation='linear')
    c2 = Curve({1:1})
    ##
    c3 = c1+c2
    c4 = c3 * c1
    ##
    from loguru import logger
    
    c5a = 5 + c3
    c5b = c3 + 5
    c6a = 5 + c4
    c6b = c4 + 5
    ##
    logger.debug("here goes nothing")
    c7a = 5 * c3
    logger.debug("we did it!")
    # c7b = c3 * 5
    # c8a = 5 * c4
    # c8b = c4 * 5
    ##
    for i in range(10):
        logger.debug(i)
        #logger.debug(f"{c5a} - {c5a.label} - this::{c5a.parameters['this']} - that::{c5a.parameters['that']} - {c5a.weight}")
        # first line is same as test_composition_of_composition
        # assert c4[i] == (c1[i] + c2[i]) * c1[i]
        # assert c5a[i] == 5 + c3[i]
        # assert c5b[i] == c3[i] + 5
        # assert c6a[i] == 5 + c4[i]
        # assert c6b[i] == c4[i] + 5
        ##
        assert c7a[i] == 5 * c3[i]
        # assert c7b[i] == c3[i] * 5
        # assert c8a[i] == 5 * c4[i]
        # assert c8b[i] == c4[i] * 5