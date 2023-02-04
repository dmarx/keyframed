from .curve import (
    Composition,
    Curve,
    Keyframe,
    ParameterGroup,
    #SmoothCurve,
)
from .interpolation import (
    bisect_left_keyframe, 
    bisect_right_keyframe, 
    register_interpolation_method,
)


def SmoothCurve(*args, **kargs):
    """
    Thin wrapper around the Curve class that uses an 'eased_lerp' for `default_interpolation` to produce a smooth curve
    instead of a step function. In the future, the interpolation function on this class may be modified to use a different
    smoothing interpolator.
    """
    return Curve(*args, default_interpolation='eased_lerp', **kargs)


__all__ = [
    'bisect_left_keyframe',
    'bisect_right_keyframe',
    'Composition',
    'Curve',
    'Keyframe',
    'ParameterGroup',
    'register_interpolation_method',
    'SmoothCurve',
    ]