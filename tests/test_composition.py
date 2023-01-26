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

    additive = Composition(pg, reduction=lambda x,y: x+y)
    multiplicative =  Composition(pg, reduction=lambda x,y: x*y)
    
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
    #c1[1]=2
    #for i in range(10):
    #    assert (c1[i] + c2[i]) == c3[i]
    #    assert (c2[i] + c1[i]) == c3[i]


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
    #c1[1]=3
    #for i in range(10):
    #    assert (c1[i] * c2[i]) == c3[i]
    #    assert (c2[i] * c1[i]) == c3[i]

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

#############

def test_composition_of_copmosition():
    c1 = Curve({1:1}, default_interpolation='linear')
    c2 = Curve({1:1})
    c3 = c1+c2
    c4 = c3 * c1
    for i in range(10):
        assert c4[i] == (c1[i] + c2[i]) * c1[i]