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


import math

class SinusoidalCurve(Curve):
    def __init__(
        self,
        frequency=None,
        wavelength=None,
        phase=0,
        amplitude=1,
    ):
        if ((frequency is None) and (wavelength is None)) or (
            (frequency is not None) and (wavelength is not None)
        ):
            raise TypeError("To initialize a SinusoidalCurve, one of frequency of wavelength must be provided.")
        #if (wavelength is not None) and (frequency is None):
            #frequency = 1/wavelength
        #self.frequency = frequency
        if (frequency is not None) and (wavelength is None):
            wavelength = 1/frequency
        self.wavelength = wavelength
        self.phase = phase
        self.amplitude = amplitude
        super().__init__(default_interpolation=self._f)
    def _f(self, k, self_again):
        """internal parameterization of sine function to use as interpolator"""
        return self.amplitude * math.sin(2*math.pi*k / self.wavelength + self.phase)
    @property
    def frequency(self):
        return 1 / self.wavelength



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