# Introduction

Welcome to the Keyframed library! This library is designed to allow you to specify and interpolate data at keyframes, and provide a variety of interpolation options.

In this library, a "keyframe" is a specific point in your data that has a defined value. For example, if you have a series of numbers that represent the positions of a moving object at specific times, each of those position measurements is a keyframe.

To use this library, you will first need to create a Keyframed object. You can do this by calling the Keyframed constructor and passing it either a dictionary of keyframes. For example:

```python
from keyframed import Keyframed

# Create a Keyframed object with three keyframes at indices 0, 5, and 10
k = Keyframed({0: 10, 5: 20, 10: 30})
```

Once you have created a Keyframed object, you can access the value at any point in the data series by using the square bracket operator ([]). If the point you are accessing is a keyframe, the value of the keyframe will be returned. If the point you are accessing is not a keyframe, the value will be interpolated based on the values of the surrounding keyframes.

For example:

```python
k = Keyframed({0: 10, 5: 20, 10: 30})

print(k[0])  # 10
print(k[5])  # 20
print(k[10])  # 30
print(k[3])  # Interpolated value between 10 and 20
```

You can also set the value of a keyframe by using the square bracket operator and assignment. For example:

```python
k = Keyframed({0: 10, 5: 20, 10: 30})
k[15] = 40

print(k[15])  # 40
```


By default, the Keyframed object will use `previous` interpolation to calculate values between keyframes, i.e. it will check the value for the previous frame and use that to fill the current frame. All interpolation methods supported by the 'kind' argument of `scipy.interpolate.interp1d` are supported out-of-the box, just ask for them by name

 # Non-standard interpolation


You can also specify a callable function as the value for a keyframe. This function should take two arguments: the index of the keyframe being accessed and the Keyframed object itself. The function can then use the values of other keyframes to calculate the value for the keyframe being accessed. For example:

```python
def fibonacci(k, K):
    return K[k-1] + K[k-2]

k = Keyframed({0: 1, 1: 1})
k[2] = fibonacci  # Set the value of keyframe 2 using the fibonacci function

print(k[2])  # 2
print(k[3])  # 3
print(k[4])  # 5
```

In addition to the basic functionality described above, the Key

In addition to the basic functionality described above, the Keyframed object also provides a Looper wrapper to facilitate using Keyframed objects to parameterize loops, such as Low-Frequency Oscillators (LFOs). The Looper wrapper takes a Keyframed object as its input and can be set to repeat the Keyframed sequence for a certain number of repetitions or indefinitely. The Looper can also be set to become active at a certain point in the sequence.

To create a Looper, you first need to create a Keyframed object with the desired sequence of keyframes and interpolation methods. Then, you can wrap the Keyframed object in a Looper object by calling the Looper constructor with the Keyframed object as its input. The Looper object has several optional arguments, including max_repetitions, activate_at, and deactivate_at, which allow you to specify the number of repetitions, the point at which the Looper becomes active, and the point at which the Looper becomes deactivated, respectively.

Here is an example of creating a Looper object with a Keyframed object that has a sawtooth waveform and becomes active at the fifth repetition:

```python
from keyframed import Keyframed
from keyframed.wrappers import Looper

# Create a Keyframed object with a sawtooth waveform
keyframed = Keyframed({0: 0, 4: 10}, interp={0: 'linear'}, n=5)

# Wrap the Keyframed object in a Looper object
looper = Looper(keyframed, max_repetitions=5, activate_at=5)

# The Looper object is now active and will repeat the Keyframed sequence for a total of 25 steps
print(looper[0])  # Output: 0
print(looper[24])  # Output: 10
print(looper[25])  # Output: 0
```

You can also use the Looper.resolve() method to flatten the Looper object into a Keyframed object with the full sequence of values. This can be useful if you want to access the full sequence of values without the Looper's active and deactive behavior. Here is an example of using Looper.resolve() to flatten a Looper object:

```python
from keyframed import Keyframed
from keyframed.wrappers import Looper

# Create a Keyframed object with a sawtooth waveform
keyframed = Keyframed({0: 0, 4: 10}, interp={0: 'linear'}, n=5)

# Wrap the Keyframed object in a Looper object
looper = Looper(keyframed, max_repetitions=5, activate_at=5)

# Flatten the Looper object into a Keyframed object
keyframed_flattened = looper.resolve()

# The Keyframed object now contains the full sequence of values from the Looper object
print(keyframed_flattened[0])  # Output: 0
print(keyframed_flattened[24])  # Output: 10
print(keyframed_flattened[25])  # Output: 0
```

In addition to the Keyframed and Looper classes, the Keyframed library also provides an Adaptor class that allows you to adapt a Keyframed object to

In addition to the Keyframed and Looper classes, this library provides a number of utility functions and decorators that can be used to customize and extend the behavior of your keyframed objects.

For example, the frameContext decorator allows you to specify a window of keyframes around the current frame when defining a getter function. This can be useful when you want to use the values of several surrounding keyframes to calculate the value of the current frame.

The Adaptor class provides a way to transform the output of a keyframed object in a variety of ways, such as scaling, reversing, or looping. You can also use the Adaptor class to "freeze" the current state of a keyframed object by wrapping it in an adaptor and setting its freeze attribute to True.

In addition to these utility functions and classes, this library also provides a number of built-in interpolation methods that you can use when defining your keyframed objects. These include linear, quadratic, and cubic interpolation, as well as a number of other options.

Overall, this library provides a flexible and intuitive way to create and manipulate keyframed data, making it a useful tool for a wide variety of applications. Whether you're working on a music or video project, creating animations, or just want to experiment with keyframing in general, this library is a great choice.
