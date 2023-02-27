"""
Misc useful pre-built stuff
"""
import math
from .curve import (
    Composition,
    Curve,
)
from .interpolation import (
    bisect_left_keyframe, 
)


def SmoothCurve(*args, **kargs):
    """
    Thin wrapper around the Curve class that uses an 'eased_lerp' for `default_interpolation` to produce a smooth curve
    instead of a step function. In the future, the interpolation function on this class may be modified to use a different
    smoothing interpolator.
    """
    return Curve(*args, default_interpolation='eased_lerp', **kargs)


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


class HawkesProcessIntensity(Composition):
    """
    Parameterizes the intensity function of a hawkes process, i.e. a self-exciting point-process.
    Can be interpreted as a pseudo-counting function where the influence of older events is subjected to
    exponential decay.
    """
    def __init__(
        self,
        events=None,
        reduction='sum',
        decay=0.05,
        *args, **kargs,
    ):
        self.decay=decay
        super().__init__(*args, **kargs, reduction=reduction, parameters={})
        if events is not None:
            for e in events:
              self.add_event(e)

    def add_event(self, t):
        c = Curve({0:0}, default_interpolation=self.decay_fn)
        c[t] = 1
        self.parameters[t] = c

    def decay_fn(self, t, curve):
        kf_prev = bisect_left_keyframe(t, curve)
        td = max(t- kf_prev.t, 0)
        v0 = kf_prev.value
        return v0 * math.exp(-td * self.decay)

