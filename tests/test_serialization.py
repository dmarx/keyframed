import pytest
from keyframed import Curve, ParameterGroup, register_interpolation_method, Keyframe, Composition, from_yaml

from omegaconf import OmegaConf

# NB: because of how __eq__ is implemented, the from_dict tests will only work correctly
#     if the corresponding to_dict methods work correctly. ergo, need to make sure the
#     to_dict tests are rigorous

TEST_EPS = 1e-8

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
    #     weight=Curve(1), # wait a second... here's our problem, duh. Is this still a thing? cause that's not a dict.
    # )
    d = pg.to_dict(simplify=False)
    assert list(d['parameters'].keys()) == ['a','b']
    assert list(d['weight'].keys()) == ['curve','loop','duration','label']
    assert d['weight']['curve'][0] ==  {'interpolation_method': 'previous', 't': 0, 'value': 1}


def test_pgroup_from_dict():
    c0 = Curve({1:1,5:5})
    c1 = Curve({2:3,7:6})
    pg = ParameterGroup({'a':c0,'b':c1})
    d = pg.to_dict(simplify=True)
    pg2 = ParameterGroup.from_dict(d)
    assert pg == pg2
    assert pg[2] == pg2[2] == {'a':1, 'b':3}

def test_pgroup_from_dict_verbose():
    c0 = Curve({1:1,5:5})
    c1 = Curve({2:3,7:6})
    pg = ParameterGroup({'a':c0,'b':c1})
    d = pg.to_dict(simplify=False)
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

def test_composition_of_copmosition_to_dict():
    c1 = Curve({1:1}, default_interpolation='linear')
    c2 = Curve({1:1})
    c3 = c1+c2
    c4 = c3 * c1
    d = c4.to_dict()
    assert d == {'weight': {'composition': {'this': {0: 1}, 'this1': {'default_interpolation': 'linear', 1: 1}}, 'reduction_name': 'product'}, 'composition': {'this': {'default_interpolation': 'linear', 1: 1}, 'that': {1: 1}}, 'reduction_name': 'sum'}

def test_curve_to_dict_with_nonstandard_default_interpolator():
    c1 = Curve({1:1}, default_interpolation='linear')
    d = c1.to_dict(simplify=False)
    assert d == {'curve': {0: {'t': 0, 'value': 0, 'interpolation_method': 'linear'}, 1: {'t': 1, 'value': 1, 'interpolation_method': 'linear'}}, 'loop': False, 'duration': 1, 'label': None}
    d = c1.to_dict(simplify=True)
    assert d == {'default_interpolation': 'linear', 1: 1}


def test_curve_from_dict_with_nonstandard_default_interpolator():
    c1 = Curve({1:1}, default_interpolation='linear')
    d = c1.to_dict(simplify=True)
    c2 = Curve.from_dict(d)
    for i in range(10):
        assert c1[i] == c2[i]

def test_curve2dict_w_kf_specified_interpolator():
    c1 = Curve({0:1, 5:Keyframe(t=5,value=1,interpolation_method='linear'), 9:5})
    d = c1.to_dict(simplify=True)
    print(d)
    assert c1[7] == 3
    c2 = Curve.from_dict(d)
    for i in range(10):
        assert c1[i] == c2[i]

def test_curve2dict_with_nonstandard_default_interpolator_and_kf_specified_interpolator():
    c1 = Curve({0:1, 5:Keyframe(t=5,value=6,interpolation_method='previous'), 9:5}, default_interpolation='linear')
    d = c1.to_dict(simplify=True)
    print(d)
    assert abs(c1[1] - 2) < TEST_EPS
    assert c1[7] == 6
    c2 = Curve.from_dict(d)
    for i in range(10):
        assert c1[i] == c2[i]


def test_simplified_curvesum():
    c0 = Curve(1)
    c1 = Curve(2)

    c2 = c0 + c1
    d = c2.to_dict(simplify=True)
    #assert d == {'composition': {'parameters': {'this': {0: 1}, 'that': {0: 2}}}, 'reduction_name': 'sum'}
    assert d == {'composition': {'this': {0: 1}, 'that': {0: 2}}, 'reduction_name': 'sum'}


def test_read_yaml():
    # target_yaml = """curves:
    # mycurve:
    #     0: 0
    #     1: 1
    #     3: 5
    #     loop: true
    #     duration: 3"""
    target_yaml = """curves:
- 0: 1
  100: 0"""
    #curves = Curve.from_yaml(target_yaml2)
    #c1 = Curve({0:1, 5:Keyframe(t=5,value=6,interpolation_method='previous'), 9:5}, default_interpolation='linear')
    #c1 = Curve({0:1, 100:0})
    #d = c1.to_dict(simplify=True)
    #cfg = OmegaConf.create({'curves':[d]})
    #yaml = OmegaConf.to_yaml(cfg)
    #print(target_yaml)
    #raise
    curves = from_yaml(target_yaml)
    c1 = Curve({0:1, 100:0})
    assert curves == [c1]


def test_read_yaml2():
    target_yaml = """curves:
  - 0: 1
    100: 0
  - loop: true
    default_interpolation: linear
    1: 2
    2: 3
"""
    curves = from_yaml(target_yaml)
    c1 = Curve({0:1, 100:0})
    c2 = Curve({1:2,2:3},loop=True,default_interpolation='linear')
    assert curves == [c1,c2]

def test_read_yaml3():
    target_yaml = """curves:
  foo:
    0: 1
    100: 0
  bar:
    1: 2
    2: 3
    loop: true
    default_interpolation: linear
"""
    #curves = from_yaml(target_yaml)
    #print(curves)
    #raise
    c1 = Curve({0:1, 100:0}, label='foo')
    c2 = Curve({1:2,2:3},loop=True,default_interpolation='linear', label='bar')
    cfg = OmegaConf.create([c1.to_dict(), c2.to_dict()])
    print(OmegaConf.to_yaml(cfg)) # labels getting dropped by Curve.to_dict()
    raise
    #assert curves == [c1,c2]