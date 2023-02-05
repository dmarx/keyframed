from .curve import Keyframe, Curve, CurveBase, ParameterGroup, Composition

def _is_keyframe(d:dict):
    if len(d) != 3:
        return False
    if not all(k in d for k in ('t', 'value', 'interpolation_method')):
        return False
    return True


def from_dict(d:dict):
    # assume fully saturated dict
    if _is_keyframe(d):
        return Keyframe(**d)
    raise NotImplementedError