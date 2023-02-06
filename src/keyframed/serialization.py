from .curve import Keyframe, Curve, CurveBase, ParameterGroup, Composition

def test_type_by_keys(d:dict, keys):
    assert isinstance(d, dict)
    if len(d) != len(keys):
        return False
    if not all(k in d for k in keys):
        return False
    return True

ATTRS_BY_TYPE ={
    'Keyframe': ('t', 'value', 'interpolation_method'),
    'Curve':('curve', 'duration', 'label', 'loop'),
    'ParameterGroup':('parameters', 'duration', 'label', 'loop'),
    'Composition':('parameters', 'duration', 'label', 'loop', 'reduction'),
}

def _is_keyframe(d:dict):
    return test_type_by_keys(d, ATTRS_BY_TYPE['Keyframe'])

def _is_curve(d:dict):
    return test_type_by_keys(d, ATTRS_BY_TYPE['Curve'])
    
def _is_pgroup(d:dict):
    return test_type_by_keys(d, ATTRS_BY_TYPE['ParameterGroup']) 
    # can pgroups loop? if not, i should change that. 
    # Maybe I should rename ParameterGroup -> Track?
    # user friendly API: wrap a pgroup in a "TimeLine" class, user's can add curves using abstracted api. 
    # forces users to name things uniquely etc.

def _is_comp(d:dict):
    return test_type_by_keys(d, ATTRS_BY_TYPE['Composition']) 

def from_dict(d:dict):
    # assume fully saturated dict
    if _is_keyframe(d):
        return Keyframe(**d)
    if _is_curve(d):
        return Curve(**d)
    
    if _is_pgroup(d):
        pass
        d_ = {}
        pgroup_attrs = ()
        for k, v in d.items():
            if k not in pgroup_attrs:
                v = from_dict(v)
            d_[k] = v
        return d_

    if _is_comp(d):
        pass

    raise NotImplementedError
