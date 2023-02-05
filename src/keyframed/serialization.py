from .curve import Keyframe, Curve, CurveBase, ParameterGroup, Composition

def test_type_by_keys(d:dict, keys):
    assert isinstance(d, dict)
    if len(d) != len(keys):
        return False
    if not all(k in d for k in keys):
        return False
    return True

def _is_keyframe(d:dict):
    return test_type_by_keys(d, ('t', 'value', 'interpolation_method'))

def _is_curve(d:dict):
    return test_type_by_keys(d, ('curve', 'duration', 'label', 'loop'))
    


def from_dict(d:dict):
    # assume fully saturated dict
    if _is_keyframe(d):
        return Keyframe(**d)
    if _is_curve(d):
        return Curve(**d)
    raise NotImplementedError