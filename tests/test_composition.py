from keyframed import ParameterGroup, Curve, SmoothCurve, Composition

EPS = 1e-9

def test_composition_direct():

    kfs = {0:0,1:1,10:10}
    pg = ParameterGroup({
        'stepfunc':Curve(kfs),
        'smoothfunc':SmoothCurve(kfs),
        'longstep':Curve({0:1, 15:15}),
    })

    additive = Composition(pg, lambda x,y: x+y)
    multiplicative =  Composition(pg, lambda x,y: x*y)
    
    assert abs(additive[4] - 5.25) < EPS
    assert abs(multiplicative[4] - 3.25) < EPS


def test_add_curves():
    pass

def test_add_loop_to_curve():
    pass

def test_add_loop_to_loop():
    pass


def test_mul_curves():
    pass

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