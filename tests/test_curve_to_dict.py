import pytest
from keyframed import Curve, ParameterGroup, register_interpolation_method, Keyframe, Composition

#from omegaconf import OmegaConf


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
    assert d['label'].startswith('curve_')


def test_curve_to_dict_w_interpolation():
    curve = {1:1,3:Keyframe(t=3,value=5,interpolation_method='linear'), 10:12}
    c = Curve(curve=curve, loop=True, label='foobar')
    d = c.to_dict(simplify=False)
    print(d)
    assert d == {'curve': {0: {'t': 0, 'value': 0, 'interpolation_method': 'previous'}, 1: {'t': 1, 'value': 1, 'interpolation_method': 'previous'}, 3: {'t': 3, 'value': 5, 'interpolation_method': 'linear'}, 10: {'t': 10, 'value': 12, 'interpolation_method': 'linear'}}, 'loop': True, 'duration': 10, 'label': 'foobar'}


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



def test_composition_to_dict():
    c0 = Curve({1:1,5:5}, label='foo')
    c1 = Curve({2:3,7:6}, label='bar')
    pg = ParameterGroup({'a':c0,'b':c1}, label='baz')
    comp = Composition(parameters=pg, reduction='sumfunc', label='boink')
    d = comp.to_dict()
    print(d)
    assert d == {'parameters': {'a': {'curve': {0: {'t': 0, 'value': 0, 'interpolation_method': 'previous'}, 1: {'t': 1, 'value': 1, 'interpolation_method': 'previous'}, 5: {'t': 5, 'value': 5, 'interpolation_method': 'previous'}}, 'loop': False, 'duration': 5, 'label': 'a'}, 'b': {'curve': {0: {'t': 0, 'value': 0, 'interpolation_method': 'previous'}, 2: {'t': 2, 'value': 3, 'interpolation_method': 'previous'}, 7: {'t': 7, 'value': 6, 'interpolation_method': 'previous'}}, 'loop': False, 'duration': 7, 'label': 'b'}}, 'weight': {'curve': {0: {'t': 0, 'value': 1, 'interpolation_method': 'previous'}}, 'loop': False, 'duration': 0, 'label': 'boink_WEIGHT'}, 'label': 'boink', 'reduction': 'sumfunc'}



def test_composition_of_composition_to_dict():
    c1 = Curve({1:1}, label='foo', default_interpolation='linear')
    c2 = Curve({1:1}, label='bar')
    c3 = c1+c2
    print(c3.label)
    print(c3.weight.label)
    c4 = c3 * c1    
    d = c4.to_dict()
    assert c4.label.startswith('prod(foo+bar, foo)_')
    c4.label = 'dummy'
    #c4.weight.label = 'dummy_weight'
    #print((c4.label, c3.label, c2.label, c1.label))
    #print('dummy' in str(c4.to_dict()))
    #print(c4.to_dict())
    d2 = c4.to_dict()
    assert d2 == {'parameters': {'foo+bar': {'parameters': {'foo': {'curve': {0: {'t': 0, 'value': 0, 'interpolation_method': 'linear'}, 1: {'t': 1, 'value': 1, 'interpolation_method': 'linear'}}, 'loop': False, 'duration': 1, 'label': 'foo'}, 'bar': {'curve': {0: {'t': 0, 'value': 0, 'interpolation_method': 'previous'}, 1: {'t': 1, 'value': 1, 'interpolation_method': 'previous'}}, 'loop': False, 'duration': 1, 'label': 'bar'}}, 'weight': {'curve': {0: {'t': 0, 'value': 1, 'interpolation_method': 'previous'}}, 'loop': False, 'duration': 0, 'label': 'foo+bar_WEIGHT'}, 'label': 'foo+bar', 'reduction': 'add'}, 'foo': {'curve': {0: {'t': 0, 'value': 0, 'interpolation_method': 'linear'}, 1: {'t': 1, 'value': 1, 'interpolation_method': 'linear'}}, 'loop': False, 'duration': 1, 'label': 'foo'}}, 'weight': {'curve': {0: {'t': 0, 'value': 1, 'interpolation_method': 'previous'}}, 'loop': False, 'duration': 0, 'label': 'dummy_WEIGHT'}, 'label': 'dummy', 'reduction': 'prod'}


def test_curve_to_dict_with_nonstandard_default_interpolator():
    c1 = Curve({1:1}, label='foo', default_interpolation='linear')
    d = c1.to_dict(simplify=False)
    print(d)
    assert d == {'curve': {0: {'t': 0, 'value': 0, 'interpolation_method': 'linear'}, 1: {'t': 1, 'value': 1, 'interpolation_method': 'linear'}}, 'loop': False, 'duration': 1, 'label': 'foo'}
    #d = c1.to_dict(simplify=True)
    #assert d == {'default_interpolation': 'linear', 1: 1}

##################################################################################


def test_curve_to_yamldict():
    c1 = Curve({1:1}, label='foo', default_interpolation='linear')
    d = c1.to_dict(simplify=False, for_yaml=True)
    assert d == {'curve': ((0, 0, 'linear'), (1, 1, 'linear')), 'loop': False, 'duration': 1, 'label': 'foo'}

from keyframed.serialization import from_dict

def test_curve_from_yamldict():
    c1 = Curve({1:1}, label='foo', default_interpolation='linear')
    d = c1.to_dict(simplify=False, for_yaml=True)
    assert d == {'curve': ((0, 0, 'linear'), (1, 1, 'linear')), 'loop': False, 'duration': 1, 'label': 'foo'}
    c2 = from_dict(d)
    assert c1 == c2

##################################################################################

# def test_curve2dict_w_kf_specified_interpolator():
#     c1 = Curve({0:1, 5:Keyframe(t=5,value=1,interpolation_method='linear'), 9:5})
#     d = c1.to_dict(simplify=True)
#     print(d)
#     assert c1[7] == 3
#     c2 = Curve.from_dict(d)
#     for i in range(10):
#         assert c1[i] == c2[i]

# def test_curve2dict_with_nonstandard_default_interpolator_and_kf_specified_interpolator():
#     c1 = Curve({0:1, 5:Keyframe(t=5,value=6,interpolation_method='previous'), 9:5}, default_interpolation='linear')
#     d = c1.to_dict(simplify=True)
#     print(d)
#     assert abs(c1[1] - 2) < TEST_EPS
#     assert c1[7] == 6
#     c2 = Curve.from_dict(d)
#     for i in range(10):
#         assert c1[i] == c2[i]

######################################################


# def test_curve_from_dict_with_nonstandard_default_interpolator():
#     c1 = Curve({1:1}, default_interpolation='linear')
#     d = c1.to_dict(simplify=True)
#     c2 = Curve.from_dict(d)
#     for i in range(10):
#         assert c1[i] == c2[i]

# def test_curve_from_dict():
#     curve = {1:1,3:5}
#     c = Curve(curve=curve, loop=True)
#     d = c.to_dict(simplify=False)
#     c2 = Curve.from_dict(d)
#     assert c == c2
#     assert c.loop and c2.loop

# def test_pgroup_from_dict():
#     c0 = Curve({1:1,5:5})
#     c1 = Curve({2:3,7:6})
#     pg = ParameterGroup({'a':c0,'b':c1})
#     d = pg.to_dict(simplify=True)
#     pg2 = ParameterGroup.from_dict(d)
#     assert pg == pg2
#     assert pg[2] == pg2[2] == {'a':1, 'b':3}

# def test_pgroup_from_dict_verbose():
#     c0 = Curve({1:1,5:5})
#     c1 = Curve({2:3,7:6})
#     pg = ParameterGroup({'a':c0,'b':c1})
#     d = pg.to_dict(simplify=False)
#     pg2 = ParameterGroup.from_dict(d)
#     assert pg == pg2


# def test_curvesum_from_dict():
#     c0 = Curve({1:1,5:5})
#     c1 = Curve({2:3,7:6})
#     comp = c0 + c1
#     d = comp.to_dict()
#     assert d == {'composition': {'this': {1: 1, 5: 5}, 'that': {2: 3, 7: 6}}, 'reduction_name': 'sum'}
#     comp2 = Composition.from_dict(d)
#     assert comp == comp2

# def test_curveprod_from_dict():
#     c0 = Curve({1:1,5:5})
#     c1 = Curve({2:3,7:6})
#     comp = c0 * c1
#     d = comp.to_dict()
#     assert d == {'composition': {'this': {1: 1, 5: 5}, 'that': {2: 3, 7: 6}}, 'reduction_name': 'product'}
#     comp2 = Composition.from_dict(d)
#     assert comp == comp2


# def test_composition_via_curve_from_dict():
#     c0 = Curve({1:1,5:5})
#     c1 = Curve({2:3,7:6})
#     comp = c0 + c1
#     d = comp.to_dict()
#     assert d == {'composition': {'this': {1: 1, 5: 5}, 'that': {2: 3, 7: 6}}, 'reduction_name': 'sum'}
#     comp2 = Curve.from_dict(d)
#     assert comp == comp2
#     assert comp2[2] == 4

######################################################

# def test_simplified_curvesum():
#     c0 = Curve(1)
#     c1 = Curve(2)

#     c2 = c0 + c1
#     d = c2.to_dict(simplify=True)
#     #assert d == {'composition': {'parameters': {'this': {0: 1}, 'that': {0: 2}}}, 'reduction_name': 'sum'}
#     assert d == {'composition': {'this': {0: 1}, 'that': {0: 2}}, 'reduction_name': 'sum'}


# def test_read_yaml():
#     # target_yaml = """curves:
#     # mycurve:
#     #     0: 0
#     #     1: 1
#     #     3: 5
#     #     loop: true
#     #     duration: 3"""
#     target_yaml = """curves:
# - 0: 1
#   100: 0"""
#     #curves = Curve.from_yaml(target_yaml2)
#     #c1 = Curve({0:1, 5:Keyframe(t=5,value=6,interpolation_method='previous'), 9:5}, default_interpolation='linear')
#     #c1 = Curve({0:1, 100:0})
#     #d = c1.to_dict(simplify=True)
#     #cfg = OmegaConf.create({'curves':[d]})
#     #yaml = OmegaConf.to_yaml(cfg)
#     #print(target_yaml)
#     #raise
#     curves = from_yaml(target_yaml)
#     c1 = Curve({0:1, 100:0})
#     assert curves == [c1]


# def test_read_yaml2():
#     target_yaml = """curves:
#   - 0: 1
#     100: 0
#   - loop: true
#     default_interpolation: linear
#     1: 2
#     2: 3
# """
#     curves = from_yaml(target_yaml)
#     c1 = Curve({0:1, 100:0})
#     c2 = Curve({1:2,2:3},loop=True,default_interpolation='linear')
#     assert curves == [c1,c2]

# def test_read_yaml3():
#     target_yaml = """curves:
#   foo:
#     0: 1
#     100: 0
#   bar:
#     1: 2
#     2: 3
#     loop: true
#     default_interpolation: linear
# """
#     #curves = from_yaml(target_yaml)
#     #print(curves)
#     #raise
#     c1 = Curve({0:1, 100:0}, label='foo')
#     c2 = Curve({1:2,2:3},loop=True,default_interpolation='linear', label='bar')
#     cfg = OmegaConf.create([c1.to_dict(), c2.to_dict()])
#     print(OmegaConf.to_yaml(cfg)) # labels getting dropped by Curve.to_dict()
#     raise
#     #assert curves == [c1,c2]