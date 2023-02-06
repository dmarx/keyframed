from keyframed.serialization import from_dict
from keyframed import Keyframe, Curve, ParameterGroup, Composition

def test_kf_from_dict():
    kf = Keyframe(t=0, value=1, interpolation_method='foobar')
    d = kf.to_dict()
    kf2 = from_dict(d)
    assert kf2.t == kf.t
    assert kf2.value == kf.value
    assert kf2.interpolation_method == kf.interpolation_method

def test_curve_from_dict():
    c = Curve(1, label='foo')
    d = c.to_dict()
    c2 = from_dict(d)
    assert c.label == c2.label
    assert c.loop == c2.loop
    assert c.duration == c2.duration
    assert c._data == c2._data # NB: __eq__ ignores interpolation methods I think
    assert c == c2

def test_pgroup_curves_from_dict():
    c1 = Curve(label='foo')
    c2 = Curve(label='bar')
    c3 = ParameterGroup((c1, c2))
    d = c3.to_dict()
    print(d)
    print(d.keys())
    c4 = from_dict(d)
    print(c4)
    #raise
    # to do: add equality methods to the classes
    assert c3 == c4
    # this really deserves its own separate test (for __eq__)
    c3.label = 'baz'
    assert c1 != c4

############################################

# this is a duplicate of a test in test_curve_to_dict
# def test_curve_from_yamldict():
#     c1 = Curve({1:1}, label='foo', default_interpolation='linear')
#     d = c1.to_dict(simplify=False, for_yaml=True)
#     assert d == {'curve': ((0, 0, 'linear'), (1, 1, 'linear')), 'loop': False, 'duration': 1, 'label': 'foo'}
#     c2 = from_dict(d)
#     assert c1 == c2

def test_pgroup_from_yamldict():
    c1 = Curve(label='foo')
    c2 = Curve(label='bar')
    c3 = ParameterGroup((c1, c2))
    d = c3.to_dict(simplify=False, for_yaml=True)
    print(d)
    assert d == {'parameters': {'foo': {'curve': ((0, 0, 'previous'),), 'loop': False, 'duration': 0, 'label': 'foo'}, 'bar': {'curve': ((0, 0, 'previous'),), 'loop': False, 'duration': 0, 'label': 'bar'}}, 'weight': {'curve': ((0, 1, 'previous'),), 'loop': False, 'duration': 0, 'label': 'pgroup(foo,bar)_WEIGHT'}, 'label': 'pgroup(foo,bar)'}
    c4 = from_dict(d)
    assert c3 == c4

from keyframed import SmoothCurve

def test_compositional_pgroup_from_yamldict():
    low, high = 0.0001, 0.3
    step1 = 50
    step2 = 2 * step1
    curves = ParameterGroup((
        SmoothCurve({0:low, (step1-1):high, (2*step1-1):low}, loop=True),
        SmoothCurve({0:high, (step1-1):low, (2*step1-1):high}, loop=True),

        SmoothCurve({0:low, (step2-1):high, (2*step2-1):low}, loop=True),
        SmoothCurve({0:high, (step2-1):low, (2*step2-1):high}, loop=True),
    ))
    curves2 = curves + 1
    d = curves2.to_dict(simplify=False, for_yaml=True)
    curves3 = from_dict(d)
    assert curves2 == curves3