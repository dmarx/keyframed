"""
Misc useful pre-built stuff
"""
from .curve import (
    Composition,
    Curve,
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

        super().__init__(
            default_interpolation="sine_wave",
            default_interpolator_args=dict(
                amplitude=self.amplitude,
                phase=self.phase,
                wavelength=self.wavelength,
                frequency=self.frequency,
            ),
        )

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
        c = Curve(
            {0:0}, 
            default_interpolation='exp_decay', 
            default_interpolator_args={'decay_rate':self.decay}
        )
        c[t] = 1
        self.parameters[t] = c

