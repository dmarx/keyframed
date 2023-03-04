from keyframed import SinusoidalCurve, ParameterGroup, Curve, Composition

import math
import matplotlib.pyplot as plt

import pytest

def test_bug0():


    low, high = 0, 0.3
    step1 = 50
    step2 = 2 * step1

    curves = ParameterGroup((
    #SmoothCurve({0:low,  step1:high},  bounce=True),
    SinusoidalCurve(wavelength=step1*2, phase=3*math.pi/2) ,#+ Curve(high/2),
    #SmoothCurve({0:high, step1:low}, bounce=True),
    SinusoidalCurve(wavelength=step1*2, phase=math.pi/2) ,#+ Curve(high/2),
    #SmoothCurve({0:low,  step2:high},  bounce=True),
    SinusoidalCurve(wavelength=step2*2, phase=3*math.pi/2) ,#+ Curve(high/2),
    #SmoothCurve({0:high, step2:low}, bounce=True),
    SinusoidalCurve(wavelength=step2*2, phase=math.pi/2) ,#+ Curve(high/2),
    #SinusoidalCurve(wavelength=step1*4, amplitude=high/2) + high/2
    
    #SinusoidalCurve(wavelength=step1, phase=math.pi),
    #SinusoidalCurve(wavelength=step2),
    #SinusoidalCurve(wavelength=step2, phase=math.pi),
    ))


    #curves.plot(n=1000)
    #plt.show()

    # Define another curve implicitly, extrapolating from a function
    #fancy = Curve.from_function(lambda k: high + math.sin(2*k/(step1+step2)))
    #fancy = SinusoidalCurve(wavelength=(step2+step1)/math.pi) #+ .001 #Curve(1) #Curve(high),

    fancy = SinusoidalCurve(wavelength=(step2+step1)/math.pi) + Curve(high) # breaks
    # This does it too
    #fancy =  SinusoidalCurve(wavelength=(step2+step1)*math.pi) + Curve({0:high}) 

    #fancy.plot(1000)
    #fancy =  SinusoidalCurve(wavelength=(step2+step1)*math.pi) + high # the addition here just modifies the first keyframe
    #fancy =  SinusoidalCurve(wavelength=(step2+step1)*math.pi) + Curve({0:high}) # maybe the issue here is conflicting keyframes?

    #fancy =  SinusoidalCurve(wavelength=(step2+step1)*math.pi)

    #fancy.plot(1000)
    #plt.show()

    # arithmetic on curves
    curves_plus_fancy = curves + fancy +1 + Curve(high) #+ Curve(high/2)
    curves_summed_by_frame = Composition(curves_plus_fancy, reduction='sum')
    really_fancy = curves_plus_fancy / curves_summed_by_frame

    # isolate a single channel
    ## This breaks after modifying the implementation for "fancy"
    channel_name = list(really_fancy[0].keys())[-1]

    # this is not the desired behavior. remove 'with' statement to catch the bug.
    #with pytest.raises(NotImplementedError):
    print(channel_name)
#    print(really_fancy.to_dict(simplify=True))
    print(really_fancy[0]) # weird name reuse here
    print(really_fancy[0][channel_name])
    red_channel = Curve.from_function(lambda k: really_fancy[k][channel_name])
