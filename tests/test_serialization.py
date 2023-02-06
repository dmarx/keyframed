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

def test_pgroup_curves_from_dict():
    c1 = Curve(label='foo')
    c2 = Curve(label='bar')
    c3 = ParameterGroup((c1, c2))
    d = c3.to_dict()
    print(d)
    print(d.keys())
    c4 = from_dict(d)
    print(c4)
    raise
    # to do: add equality methods to the classes