from .curve import Keyframe, Curve, CurveBase, ParameterGroup, Composition

# can probably use a simpler yaml library
from omegaconf import OmegaConf

#from loguru import logger

def _test_type_by_keys(d:dict, keys):
    assert isinstance(d, dict)
    if len(d) != len(keys):
        return False
    if not all(k in d for k in keys):
        return False
    return True

ATTRS_BY_TYPE ={
    'Keyframe': ('t', 'value', 'interpolation_method'),
    'Curve':('curve', 'duration', 'label', 'loop'),
    # confirmed: pgroup doesn't have a "loop" attribute. to do.
    # ditto duration
    'ParameterGroup':('parameters', 'weight', 'label'),
    'Composition':('parameters', 'weight', 'label', 'reduction'),
}

def _is_keyframe_dict(d:dict):
    return _test_type_by_keys(d, ATTRS_BY_TYPE['Keyframe'])

from numbers import Number

def _is_keyframe_tuple(d:tuple):
    if not isinstance(d, tuple):
        return False
    if not ( (len(d) == 2 ) or (len(d) == 3) ):
        return False
    if not isinstance(d[0], Number):
        return False
    if not isinstance(d[1], Number):
        return False
    if len(d) == 3:
        if not isinstance(d[2], str):
            print(d)
            raise TypeError(
                "length 3 tuple, assuming it's a keyframe. "
                "third element of tuple must be a string for simple serialization. "
                "just use pickle. "
                "\n...or if this error wasn't thrown because you were trying to serialize a curve "
                "that has a callable function for an interpolation method on one of its keyframes, "
                "please report the circumstances under which you received this error to "
                "https://github.com/dmarx/keyframed/issues/new"
            )
    return True

def _is_curve(d:dict):
    return 'curve' in d
    
def _is_pgroup(d:dict):
    #return _test_type_by_keys(d, ATTRS_BY_TYPE['ParameterGroup']) 
    # can pgroups loop? if not, i should change that. 
    # Maybe I should rename ParameterGroup -> Track?
    # user friendly API: wrap a pgroup in a "TimeLine" class, user's can add curves using abstracted api. 
    # forces users to name things uniquely etc.
    return ( ('parameters') in d and ('reduction' not in d) )

def _is_comp(d:dict):
    return ( ('parameters') in d and ('reduction' in d) )

def from_dict(d:dict):
    if _is_keyframe_dict(d):
        return Keyframe(**d)
    if _is_keyframe_tuple(d):
        return Keyframe(*d)
    if _is_curve(d):
        return Curve(**d)
    
    if _is_pgroup(d) or _is_comp(d):
        d_ = {}
        if d.get('label') is not None:
            d_['label'] = d['label']
        if d.get('weight') is not None:
            d_['weight'] = from_dict(d['weight'])

        curves = {}
        for k,v in d['parameters'].items():
            curves[k] = from_dict(v)
        d_['parameters'] = curves

        if not _is_comp(d):
            return ParameterGroup(**d_)
        else:
            d_['reduction'] = d['reduction']
            return Composition(**d_)

    raise NotImplementedError

def to_yaml(obj:CurveBase, simplify=True):
    d = obj.to_dict(simplify=simplify, for_yaml=True)
    cfg = OmegaConf.create(d)
    return OmegaConf.to_yaml(cfg)

def from_yaml(yaml_str:str):
    cfg = OmegaConf.create(yaml_str)
    d = OmegaConf.to_container(cfg)
    return from_dict(d)