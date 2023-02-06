from .curve import Keyframe, Curve, CurveBase, ParameterGroup, Composition

# can probably use a simpler yaml library
from omegaconf import OmegaConf

from loguru import logger

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
    #'ParameterGroup':('parameters', 'duration', 'label', 'loop'),
    #'Composition':('parameters', 'duration', 'label', 'loop', 'reduction'),
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

# def _is_keyframe(d:dict):
#     test1 = _is_keyframe_dict(d)
#     test2 = _is_keyframe_tuple(d)
#     return test1

def _is_curve(d:dict):
    return _test_type_by_keys(d, ATTRS_BY_TYPE['Curve'])
    
def _is_pgroup(d:dict):
    return _test_type_by_keys(d, ATTRS_BY_TYPE['ParameterGroup']) 
    # can pgroups loop? if not, i should change that. 
    # Maybe I should rename ParameterGroup -> Track?
    # user friendly API: wrap a pgroup in a "TimeLine" class, user's can add curves using abstracted api. 
    # forces users to name things uniquely etc.

def _is_comp(d:dict):
    return _test_type_by_keys(d, ATTRS_BY_TYPE['Composition']) 

def from_dict(d:dict):
    logger.debug(d)
    # assume fully saturated dict
    #if _is_keyframe(d):
    if _is_keyframe_dict(d):
        return Keyframe(**d)
    if _is_keyframe_tuple(d):
        return Keyframe(*d)
    if _is_curve(d):
        return Curve(**d)
    
    if _is_pgroup(d):
        #pass
        d_ = dict(
            label=d['label'],
            weight=from_dict(d['weight'])
        )
        curves = {}
        for k,v in d['parameters'].items():
            curves[k] = from_dict(v)
        d_['parameters'] = curves

        logger.debug(d_)
        return ParameterGroup(**d_)

    if _is_comp(d):
        pass

    raise NotImplementedError

def to_yaml(obj:CurveBase, simplify=False):
    d = obj.to_dict(simplify=simplify, for_yaml=True)
    cfg = OmegaConf.create(d)
    return OmegaConf.to_yaml(cfg)