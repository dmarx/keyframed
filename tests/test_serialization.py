import pytest
from keyframed import Curve, ParameterGroup, register_interpolation_method, Keyframe, Composition

# NB: because of how __eq__ is implemented, the from_dict tests will only work correctly
#     if the corresponding to_dict methods work correctly. ergo, need to make sure the
#     to_dict tests are rigorous

def test_kf_to_dict():
    kargs = dict(t=1,value=2,interpolation_method='linear')
    kf = Keyframe(**kargs)
    assert kf.to_dict() == kargs

def test_curve_to_dict():
    curve = {1:1,3:5}
    c = Curve(curve=curve, loop=True)
    d = c.to_dict(simplify=False)
    assert d['loop'] == True
    assert d['duration'] == 3
    assert d['label'] == None

    d = c.to_dict(simplify=True)
    print(d)
    assert 'duration' not in d
    assert 'label' not in d
    assert d['loop'] == True
    assert d[1] == 1
    assert d[3] == 5

    c.loop = False
    d = c.to_dict(simplify=True)
    assert d == curve

def test_curve_from_dict():
    curve = {1:1,3:5}
    c = Curve(curve=curve, loop=True)
    d = c.to_dict(simplify=False)
    c2 = Curve.from_dict(d)
    assert c == c2
    assert c.loop and c2.loop

def test_curve_from_dict_w_interpolation():
    curve = {1:1,3:Keyframe(t=3,value=5,interpolation_method='linear'), 10:12}
    c = Curve(curve=curve, loop=True)
    d = c.to_dict(simplify=False)
    c2 = Curve.from_dict(d)
    assert c == c2
    assert c.loop and c2.loop
    assert c[20] == c2[20] == 11


def test_pgroup_to_dict():
    c0 = Curve({1:1,5:5})
    c1 = Curve({2:3,7:6})
    pg = ParameterGroup({'a':c0,'b':c1})
    # assert pg.to_dict() == dict(
    #     parameters={'a':c0,'b':c1},
    #     weight=Curve(1),
    # )
    d = pg.to_dict(simplify=False)
    assert list(d['parameters'].keys()) == ['a','b']
    assert list(d['weight'].keys()) == ['curve','loop','duration','label']
    assert d['weight']['curve'][0] ==  {'interpolation_method': 'previous', 't': 0, 'value': 1}


def test_pgroup_from_dict():
    c0 = Curve({1:1,5:5})
    c1 = Curve({2:3,7:6})
    pg = ParameterGroup({'a':c0,'b':c1})
    #d = pg.to_dict(simplify=False) # currently fails
    d = pg.to_dict(simplify=True)
    pg2 = ParameterGroup.from_dict(d)
    assert pg == pg2


def test_composition_to_dict():
    c0 = Curve({1:1,5:5})
    c1 = Curve({2:3,7:6})
    pg = ParameterGroup({'a':c0,'b':c1})
    comp = Composition(parameters=pg)
    with pytest.raises(NotImplementedError):
        d = comp.to_dict()
    comp._reduction_name ='foo'
    d = comp.to_dict()
    assert d == {'composition': {'a': {1: 1, 5: 5}, 'b': {2: 3, 7: 6}}, 'reduction_name': 'foo'}


def test_curvesum_from_dict():
    c0 = Curve({1:1,5:5})
    c1 = Curve({2:3,7:6})
    comp = c0 + c1
    d = comp.to_dict()
    assert d == {'composition': {'this': {1: 1, 5: 5}, 'that': {2: 3, 7: 6}}, 'reduction_name': 'sum'}
    comp2 = Composition.from_dict(d)
    assert comp == comp2

def test_curveprod_from_dict():
    c0 = Curve({1:1,5:5})
    c1 = Curve({2:3,7:6})
    comp = c0 * c1
    d = comp.to_dict()
    assert d == {'composition': {'this': {1: 1, 5: 5}, 'that': {2: 3, 7: 6}}, 'reduction_name': 'product'}
    comp2 = Composition.from_dict(d)
    assert comp == comp2


def test_composition_via_curve_from_dict():
    c0 = Curve({1:1,5:5})
    c1 = Curve({2:3,7:6})
    comp = c0 + c1
    d = comp.to_dict()
    assert d == {'composition': {'this': {1: 1, 5: 5}, 'that': {2: 3, 7: 6}}, 'reduction_name': 'sum'}
    comp2 = Curve.from_dict(d)
    assert comp == comp2
    assert comp2[2] == 4

def test_read_yaml():
    target_yaml2 = """curves:
    mycurve:
        0: 0
        1: 1
        3: 5
        loop: true
        duration: 3"""
    curves = Curve.from_yaml(target_yaml2)


def test_simplified_curvesum():
    c0 = Curve(1)
    c1 = Curve(2)

    c2 = c0 + c1
    d = c2.to_dict(simplify=True)
    #assert d == {'composition': {'parameters': {'this': {0: 1}, 'that': {0: 2}}}, 'reduction_name': 'sum'}
    assert d == {'composition': {'this': {0: 1}, 'that': {0: 2}}, 'reduction_name': 'sum'}