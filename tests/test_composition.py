from keyframed import ParameterGroup, Curve, SmoothCurve, Composition
import math
import pytest

from loguru import logger

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

    additive2 = Composition((Curve(kfs), SmoothCurve(kfs), Curve({0:1, 15:15})), reduction='sum')
    assert abs(additive2[4] - 5.25) < EPS


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
    mul_curve = cos_curve * sin_curve

    xs = range(10)
    for i, x in enumerate(xs):
        assert mul_curve[x] == cos_curve[x] * sin_curve[x]

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
    c5a = 5 + c3
    c5b = c3 + 5
    c6a = 5 + c4
    c6b = c4 + 5
    ##
    logger.debug("here goes nothing")
    c7a = 5 * c3
    logger.debug("we did it!")
    c7b = c3 * 5
    c8a = 5 * c4
    c8b = c4 * 5
    ##
    for i in range(10):
        #logger.debug(i)
        #logger.debug(f"{c5a} - {c5a.label} - this::{c5a.parameters['this']} - that::{c5a.parameters['that']} - {c5a.weight}")
        #logger.debug(f"{c7a} - {c7a.label} - {c7a.weight} - {c7a.parameters} - {[str(curve) for curve in c7a.parameters.values()]}")
        # first line is same as test_composition_of_composition
        assert c4[i] == (c1[i] + c2[i]) * c1[i]
        assert c5a[i] == 5 + c3[i]
        assert c5b[i] == c3[i] + 5
        assert c6a[i] == 5 + c4[i]
        assert c6b[i] == c4[i] + 5
        ##
        assert c7a[i] == 5 * c3[i]
        assert c7b[i] == c3[i] * 5
        assert c8a[i] == 5 * c4[i]
        assert c8b[i] == c4[i] * 5

def test_mean_reduction():
    c1 = Curve({10:10}, default_interpolation='linear')
    c2 = Curve({1:1})
    #mu = Composition(c1, c2)  # to do: support composing curves passed in as a tuple. ditto parametergroups
    #mu = Composition(ParameterGroup(c1, c2)) # to do: support composing curves passed in as a tuple. ditto parametergroups
    mu = Composition({c.label:c for c in (c1, c2)}, reduction='mean')
    for i in range(10):
        assert mu[i] == (c1[i] + c2[i])/2

def test_add_pgroup_to_curve():

    n = 400
    low, high = 0.0001, 0.3
    step1 = 50
    step2 = 2 * step1

    curves = (
        SmoothCurve({0:low, (step1-1):high, (2*step1-1):low}, loop=True),
        SmoothCurve({0:high, (step1-1):low, (2*step1-1):high}, loop=True),

        SmoothCurve({0:low, (step2-1):high, (2*step2-1):low}, loop=True),
        SmoothCurve({0:high, (step2-1):low, (2*step2-1):high}, loop=True),
    )
    pgroup = ParameterGroup(curves)

    ampl = high
    # Ok i think i've figured it out and I don't have a great solution for the problem.
    # the issue here is that multiplying an integer into a curve multiplies the integer into the keyfram values, so 
    # if the curve is primarily written by the 'interpolator', the multiplication
    # gets ignored because the multiplication doesn't impact the interpolation function.
    # i think the only solution here is to coerce the multiplicand into a trivial curve and return a composition
    fancy = Curve({0:0}, default_interpolation=lambda k,_: ampl + math.sin(2*k/(step1+step2)))

    test1 = fancy + pgroup
    test2 = pgroup + fancy
    for i in range(10):
        assert test1[i] == test2[i] == {c.label:c[i] + fancy[i] for c in curves}
    
    fancy_neg = -fancy
    for i in range(1,10):
        assert fancy[i] != fancy_neg[i]
        assert fancy[i] == (-1) * fancy_neg[i]
    fancy_neg = -1*fancy
    for i in range(1,10):
        assert fancy[i] != fancy_neg[i]
        assert fancy[i] == (-1) * fancy_neg[i]
    fancy_neg = (-1)*fancy
    for i in range(1,10):
        assert fancy[i] != fancy_neg[i]
        assert fancy[i] == (-1) * fancy_neg[i]
    fancy_neg = fancy*(-1)
    for i in range(1,10):
        assert fancy[i] != fancy_neg[i]
        assert fancy[i] == (-1) * fancy_neg[i]

    test1 = fancy - pgroup
    test2 = pgroup - fancy
    for i in range(10):
        assert test1[i] == {c.label:fancy[i] - c[i] for c in curves}
        assert test2[i] == {c.label:c[i] - fancy[i] for c in curves}
    
    test1 = fancy * pgroup
    test2 = pgroup * fancy
    for i in range(10):
        assert test1[i] == test2[i] == {c.label:c[i] * fancy[i] for c in curves}

###############################################################

from keyframed.curve import DictValuesArithmeticFriendly

def test_fancy_dict():
    d = DictValuesArithmeticFriendly({'a':-1, 'b':0, 'c':1})
    assert d+1 == {'a':0,'b':1,'c':2}
    assert 1+d == {'a':0,'b':1,'c':2}
    ##
    assert d*2 == {'a':-2,'b':0,'c':2}
    assert 2*d == {'a':-2,'b':0,'c':2}
    ##
    assert d-1 == {'a':-2,'b':-1,'c':0}
    assert -1+d == {'a':-2,'b':-1,'c':0}
    ##
    assert 1-d == {'a':2, 'b':1, 'c':0}
    assert -d + 1 == {'a':2, 'b':1, 'c':0}
    ##
    assert d/2 == {'a':-1/2,'b':0,'c':1/2}
    with pytest.raises(ZeroDivisionError):
        assert 2/d == {'a':-1/2,'b':0,'c':1/2}
    d.pop('b')
    assert 2/d == {'a':-2,'c':2}

###############


def test_comp_of_loops():
    curve = Curve([(0,0),(2,2)], loop=True, default_interpolation='linear')
    comp = curve *2
    for i in range(10):
        assert comp[i] == curve[i] * 2

# def test_comp_loop():
#     curve = Curve([(0,0),(2,2)], default_interpolation='linear')
#     curve_loop = curve.copy()
#     curve_loop.loop = True
#     pgroup = ParameterGroup({'p1': curve}, loop=True)
#     for i in range(10):
#         assert pgroup[i]['p1'] == curve_loop[i]

# def test_comp_bounce():
#     curve = Curve([(0,0),(2,2)], default_interpolation='linear')
#     curve_loop = curve.copy()
#     curve_loop.bounce = True
#     pgroup = ParameterGroup({'p1': curve}, bounce=True)
#     for i in range(10):
#         assert pgroup[i]['p1'] == curve_loop[i]

# def test_comp_of_bounces():
#     curve = Curve([(0,0),(2,2)], bounce=True, default_interpolation='linear')
#     pgroup = ParameterGroup({'p1': curve})
#     for i in range(10):
#         assert pgroup[i]['p1'] == curve[i]