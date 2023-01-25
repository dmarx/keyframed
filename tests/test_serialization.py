from keyframed import Curve, ParameterGroup, register_interpolation_method, Keyframe

def test_kf_to_dict():
    kargs = dict(t=1,value=2,interpolation_method='linear')
    kf = Keyframe(**kargs)
    assert kf.to_dict() == kargs

def test_curve_to_dict():
    curve = {1:1,3:5}
    c = Curve(curve=curve, loop=True)
    d = c.to_dict()
    assert d == dict(
        curve={
            # right here, let's pop the 't' values from this
            0:{'t':0, 'value':0, 'interpolation_method':'previous'},
            1:{'t':1, 'value':1, 'interpolation_method':'previous'},
            3:{'t':3, 'value':5, 'interpolation_method':'previous'},
        },
        loop=True,
        duration=3,
        label=None,
    )

def test_pgroup_to_dict():
    pass

def test_composition_to_dict():
    pass

