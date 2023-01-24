# Keyframed: Datatypes for working with keyframed parameters

This library provides a Curve class for representing curves as a collection of keyframes.

## Summary

The main purpose of this library is to implement the `Curve` class, which can be initialized with a set of data points or a single datum. "Keyframes" are specific indices where a value is defined. You can access the data points of a Curve object by indexing it like a sequence. If the index you specify is not a keyframe (i.e., a data point that has been explicitly set), the value will be interpolated based on the surrounding keyframes. The default method of interpolation is "previous", which will simply return the value of the closest preceding keyframe. However, you can specify a different method of interpolation when setting a keyframe, or you can specify a callable function that will be used to generate the value at the given index. Curve objects also support basic arithmetic operations.

The motivation for this library is to facilitate object-oriented parameterization of generative animations, specifically working towards a replacement for the keyframing DSL developed by Chigozie Nri for parameterizing AI art animations (i.e. the keyframing syntax used by tools such as Disco Diffusion and Deforum).

## Installation

To install Keyframed, use pip:

    pip install keyframed

## Curve Construction

To create a new `Curve` object, you can pass in any of the following arguments to the `Curve` constructor:

* An integer or float: this creates a `Curve` with a single keyframe at t=0 with the given value.
* A dictionary: this creates a `Curve` with keyframes at the keys of the dictionary with the corresponding values.
* A sorted dictionary: this creates a `Curve` with the given sorted dictionary.
* A tuple: this creates a `Curve` with keyframes at the keys in the tuple with the corresponding values. The tuple should be in the format `((k0,v0), (k1,v1), ...)`.

```python
from keyframed import Curve

# create a curve with a single keyframe at t=0 with value 0
curve1 = Curve()

# create a curve with a single keyframe at t=0 with value 10
curve2 = Curve(10)

# create a curve with keyframes at t=0 and t=2 with values 0 and 2, respectively
curve3 = Curve(((0,0), (2,2)))

# create a curve with keyframes at t=0 and t=2 with values 0 and 2, respectively
curve4 = Curve({0:0, 2:2})
```

To visualize a curve, just call its `.plot()` method. Default behavior of Curve objects is to produce a step function. A versatile alternative is provided via the `SmoothCurve`, which simply has a different setting for `default_interpolation` (see more on interpolation methods and API below). Curves carry a `label` attribute: if this is populated, it will be used to label the curve in the plot.


```python
from keyframed import Curve, SmoothCurve
import matplotlib.pyplot as plt

kfs = {0:0,1:1,10:10}
c = Curve(kfs, label='stepfunc')
sc = SmoothCurve(kfs, label='smoothfunc')

c.plot()
sc.plot(linestyle='dashed')

plt.legend()
plt.show()
```

![demonstration of plot method on Curve and SmoothCurve](static/images/readme_plot1.png)


## Curve Properties

- keyframes: returns a list of the keyframes in the curve.
- values: returns a list of the values of the keyframes in the curve.

```python
curve = Curve(((0,0), (2,2)))

print(curve.keyframes)  # prints [0, 2]
print(curve.values)  # prints [0, 2]
```

## Curve Indexing

You can access the value of a keyframe in the curve by indexing the curve object with the key. If the key is not in the curve, the curve will use interpolation (defaults to 'previous') to return a value.

```python
import curve

curve = curve.Curve(((0,0), (2,2)))

print(curve[0])  # prints 0
print(curve[1])  # prints 0
print(curve[2])  # prints 2
```

## Curve Assignment

You can set the value of a keyframe in the curve by assigning to the curve object with the key. If the key is not in the curve, a new keyframe will be created.

```python
curve = Curve() # equivalent to Curve({0:0})

# set the value of the keyframe at t=0 to 10
curve[0] = 10

# set the value of the keyframe at t=1 to 20
curve[1] = 20

# set the value of the keyframe at t=2 to 30
curve[2] = 30

print(curve)  # prints "Curve({0: 10, 1: 20, 2: 30})"
```

## Keyframe Arithmetic

The `Curve` and `Keyframe` classes have magic methods implemented to support arithmetic operations on the `Keyframe.value` attribute.

```python
curve = Curve(((0,0), (2,2)))

curve1 = curve + 1
print(curve1[0]) # 1
print(curve1[1]) # 1
print(curve1[2]) # 3

curve2 = curve * 2
print(curve1[0]) # 0
print(curve1[1]) # 0
print(curve1[2]) # 4

curve3 = curve + Curve((1,1))
print(curve3[0]) # 0
print(curve3[1]) # 1
print(curve3[2]) # 3
```

## Interpolation

The Curve class defaults to "previous" interpolation, which returns the value of the keyframe to the left of the given key if the given key is not already assigned a value. Additionally, all interpolation methods of `scipy.interpolate.interp1d` are also supported (‘linear’, ‘nearest’, ‘nearest-up’, ‘zero’, ‘slinear’, ‘quadratic’, ‘cubic’, ‘next’).

```python
curve = Curve(((0,0), (2,2)))
print(curve[0]) # 0
print(curve[1]) # 0
print(curve[2]) # 2

# yes, setting t in the Keyframe object is redundant. working on it.
curve[0] = Keyframe(t=0, value=0, interpolation_method='linear')

print(curve[0]) # 0
print(curve[1]) # 1
print(curve[2]) # 2
```

You can also define custom interpolation methods. The call signature should take the a frame index as the first argument (`k`) and the Curve object itself (`curve`) as the second. You can then specify the custom method inside a `Keyframe`, assign the callable to the key directly, or register it as a named interpolation method,

```python
from keyframed import Curve, Keyframe, register_interpolation_method

def my_linear(k, curve):
    # get the leftmost and rightmost keyframe objects
    left = bisect_left_keyframe(k, curve)
    right = bisect_right_keyframe(k, curve)
    # extract x and y values from keyframe objects
    x0, x1 = left.t, right.t
    y0, y1 = left.value, right.value
    # calculate interpolation
    d = x1-x0
    t = (x1-k)/d
    outv =  t*y0 + (1-t)*y1
    return outv

curve = Curve(((0,0), (2,2)))
print(curve[0]) # 0
print(curve[1]) # 0
print(curve[2]) # 2

curve[0] = Keyframe(t=0, value=0, interpolation_method=my_linear)

print(curve[0]) # 0
print(curve[1]) # 1
print(curve[2]) # 2

# shorthand: assign the callable directly
curve = Curve(((0,0), (2,2)))
curve[0] = my_linear

print(curve[0]) # 0
print(curve[1]) # 1
print(curve[2]) # 2

# register the function to a name
register_interpolation_method('my_interpolator', my_linear)

curve = Curve(((0,0), (2,2)))
curve[0] =  Keyframe(t=0, value=0, interpolation_method='my_interpolator)

print(curve[0]) # 0
print(curve[1]) # 1
print(curve[2]) # 2
```

## Looping

The Curve class has a `loop` attribute that can be set to `True` to make the curve loop indefinitely.

```python
curve = Curve(((0,0), (1,1)), loop=True)

print(curve[0])  # prints 0
print(curve[1])  # prints 1
print(curve[2])  # prints 0
print(curve[3])  # prints 1

curve.plot(n=5)
```

![Looping step function](static/images/readme_plot_loop.png)

## Using the `ParameterGroup` class

The `ParameterGroup` class provides a convenient way to manipulate parameters together. To use it, you will first need to create a dictionary of parameters, where the keys are the names of the parameters and the values are `Curve` objects. You can then pass this dictionary to the ParameterGroup constructor, along with an optional weight parameter which can be a Curve or a Number. If not provided, the weight defaults to `Curve(value=1)`. The names provided in this dict will be used for the `label` attribute of the associated curves, overriding the curves label if one was already assigned.

```python
from keyframed import Curve, ParameterGroup

# create a dictionary of parameters
parameters = {
    "volume": Curve(0.5),
    "pitch": Curve(1.0),
    "rate": Curve(1.0),
}

# create a parameter group with a weight of 1.0
parameter_group = ParameterGroup(parameters, weight=1.0)

# access the current parameter values at key 0
print(parameter_group[0])  # {"volume": 0.5, "pitch": 1.0, "rate": 1.0}

# modify the weight parameter
parameter_group.weight *= 2.0

# access the current parameter values at key 0 again
print(parameter_group[0])  # {"volume": 1.0, "pitch": 2.0, "rate": 2.0}
```

ParameterGroups can also be used to visualize curves together. The `ParameterGroup.plot()` method
will use the duration of the longest curve in the group as the domain for the plot.

```python
from keyframed import Curve, SmoothCurve, ParameterGroup
import matplotlib.pyplot as plt

kfs = {0:0,1:1,10:10}
pg = ParameterGroup({
    'stepfunc':Curve(kfs),
    'smoothfunc':SmoothCurve(kfs),
    'longstep':Curve({15:15}),
})


pg.plot()
plt.legend()
plt.show()
```

![Plotting a ParameterGroup](static/images/readme_plot_parametergroup.png)