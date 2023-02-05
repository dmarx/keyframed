from keyframed.serialization import from_dict
from keyframed import Keyframe, Curve, ParameterGroup, Composition

def test_kf_from_dict():
    kf = Keyframe(t=0, value=1, interpolation_method='foobar')
    d = kf.to_dict()
    kf2 = from_dict(d)
    assert kf2.t == kf.t
    assert kf2.value == kf.value
    assert kf2.interpolation_method == kf.interpolation_method