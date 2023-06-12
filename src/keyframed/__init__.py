from .curve import (
    Composition,
    Curve,
    CurveBase,
    Keyframe,
    ParameterGroup,
)
from .interpolation import (
    bisect_left_keyframe, 
    bisect_right_keyframe, 
    register_interpolation_method,
)
from .misc import (
    SmoothCurve,
    SinusoidalCurve,
    HawkesProcessIntensity,
)
from .serialization import to_yaml

from .utils import simplify


__all__ = [
    'bisect_left_keyframe',
    'bisect_right_keyframe',
    'Composition',
    'Curve',
    'CurveBase',
    'HawkesProcessIntensity',
    'Keyframe',
    'ParameterGroup',
    'register_interpolation_method',
    'simplify',
    'SinusoidalCurve',
    'SmoothCurve',
    'to_yaml',
    ]