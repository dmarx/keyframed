# Introduction

Welcome to the Keyframed library! This library is designed to allow you to specify and interpolate data at keyframes, and provide a variety of interpolation options.

## Basic Concepts


- **Keyframes** - A keyframe is an index in the Keyframed object that has a specific data value associated with it. Keyframes can be specified when creating a Keyframed object using the data argument in the constructor, or they can be added later using the indexing syntax (e.g., k[10] = 3). Keyframes can be accessed directly by indexing the Keyframed object (e.g., k[10]).

- **Keyframed** - When a data value is associated with a specific index in a Keyframed object, that index is considered a "keyframe". The term "keyframed" refers to the process of specifying data values for specific indices in a Keyframed object.

- **Boundedness** - A Keyframed object can be either bounded or unbounded. A bounded Keyframed object has a fixed length, meaning that it can only store data points up to a certain index. An unbounded Keyframed object does not have a fixed length, and can store data points at any index. The boundedness of a Keyframed object is determined by the n argument in the constructor.

- **Interpolation** - Interpolation is the process of estimating a value between two known values based on their relative positions. The Keyframed class allows you to specify an interpolation method for a given index, which will be used to estimate the value of that index based on the values of

---

* Keyframes: In a Keyframed object, keyframes are specific indices where a value is defined. All other indices are filled in using interpolation.

* Keyframing: Keyframing refers to the process of defining specific values at keyframes and using interpolation to fill in values for the indices in between.

* Boundedness: A Keyframed object is said to be bounded if it has a defined length. An unbounded Keyframed object has no defined length and can be iterated indefinitely.

* Interpolation: Interpolation is the process of estimating a value between two known values. In the context of a Keyframed object, interpolation is used to estimate the values for indices between keyframes.

## Basic Usage

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


By default, the Keyframed object will use `previous` interpolation to calculate values between keyframes, i.e. it will check the value for the previous frame and use that to fill the current frame. All interpolation methods supported by the 'kind' argument of `scipy.interpolate.interp1d` are supported out-of-the box, just ask for them by name. These include linear, quadratic, and cubic interpolation, as well as a number of other options.

## Non-standard interpolation

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

## Context-aware callables

Another advanced feature of the Keyframed library is the ability to use context-aware callable data getters. These are functions that can be used to compute the data at a keyframe, but that have access to the data at a range of keyframes around the keyframe being evaluated. This can be useful when the data at a keyframe depends on the data at other keyframes in a specific context, such as a sliding window or an exponential moving average (EMA).

To use a context-aware callable data getter, you can use the frameContext decorator to specify the range of keyframes that the function should have access to. The decorator takes optional left and right parameters, which specify the number of keyframes to the left and right of the keyframe being evaluated. For example:

```python
from keyframed import frameContext

# define a context-aware callable data getter that computes the average of the data in a sliding window of length 3
@frameContext(left=1, right=1)
def windowed_avg(context, k, K: Keyframed, xs, ys):
    # `context` is a list of keyframes in the specified range around the keyframe being evaluated
    return sum([K[i] for i in context]) / len(context)

# create a new Keyframed object with some initial data
kf = Keyframed(data={0: 0, 1: 1, 3: 2, 5: 2, 6: 2, 8: 1})

# use the context-aware callable data getter to compute the average of the data in a sliding window around keyframes 2, 4, and 7
kf[2] = kf[4] = kf[7] = windowed_avg

# the data at keyframes 2, 4, and 7 should now be the average of the data in the sliding window around those keyframes
assert kf[2] == 1.5
assert kf[4] == 2
assert kf[7] == 1.5
```

## Looper

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

## Using Looper

To use Looper, you will first need to create a Keyframed object and pass it to the Looper constructor. If the Keyframed object is unbounded, Looper will automatically set its length to the length of the Keyframed object.

```python
from keyframed import Keyframed
from keyframed.wrappers import Looper

K = Keyframed({0:1, 4:10})
L = Looper(K)
```

You can then iterate over the Looper object like any other iterable.

```python
for i, value in enumerate(L):
    print(i, value)
```

This will print out the values of the Keyframed object indefinitely.

You can also specify the maximum number of repetitions that the Looper object should make using the max_repetitions argument.

```python
L = Looper(K, max_repetitions=5)
```

In this case, the Looper object will only repeat the Keyframed object 5 times before raising a StopIteration exception.

You can also specify activation and deactivation points for the Looper object using the activate_at and deactivate_at arguments. These arguments accept either a single index or a list of indices.

```python
L = Looper(K, max_repetitions=5, activate_at=5, deactivate_at=15)
```

In this case, the Looper object will only start repeating the Keyframed object at index 5 and will stop repeating it at index 15.

If you want to convert the Looper object back into a Keyframed object, you can use the resolve method. This will return a new Keyframed object that has the same values as the Looper object.

```python
K_resolved = L.resolve()
```

## Looper

The Looper is a class that wraps a Keyframed object and allows it to be used as a parameter in loops, such as low-frequency oscillators (LFOs). The Looper takes a Keyframed object as its input and adds a layer of behavior that allows the Keyframed object to be used in a loop.

### Initialization

To create a Looper, you can simply pass a Keyframed object to its constructor. For example:

```python
K = Keyframed({0:1, 9:10}, interp={0:'linear'}, n=10)
L = Looper(K)
```

If the Keyframed object is not bounded (i.e., does not have a fixed length), then the Looper will automatically set its length to the highest keyframe value plus one. For example, in the code above, the Looper will set its length to 10 because the highest keyframe value is 9.

### Activation

By default, a Looper is inactive and will not be used to parameterize a loop. However, you can specify that a Looper becomes active at a certain iteration of the loop by setting the activate_at parameter when initializing the Looper. For example:

```python
K = Keyframed({0:1, 4:10})
L = Looper(K, activate_at=5)
```

In the code above, the Looper becomes active at the 5th iteration of the loop. You can also specify a maximum number of repetitions that the Looper will be used for by setting the max_repetitions parameter. For example:

```python
K = Keyframed({0:1, 4:10})
L = Looper(K, max_repetitions=5, activate_at=5)
```

In the code above, the Looper will be used for a maximum of 5 repetitions of the loop.

### Length

The length of a Looper depends on whether it is bounded or not and whether it is active or not. If the Looper is bounded (i.e., its Keyframed object has a fixed length), then the length of the Looper will be the same as the length of its Keyframed object. If the Looper is not bounded, then its length will be determined by the max_repetitions parameter if it is active, or else it will be unbounded.

### Resolving a Looper

To use the values of a Looper in a loop, you can call its resolve() method, which returns a new Keyframed object with the values of the Looper at each iteration of the loop. For example:

```python
K = Keyframed({0:1, 4:10})
L = Looper(K, max_repetitions=5, activate_at=5)
L_flattened = L.resolve()
```

In the code above, the L_flattened object is a Keyframed object with the same length as the Looper (25 in this case) and contains the values of the Looper at each iteration of the loop.


## Adaptor

In addition to the Keyframed and Looper classes, the Keyframed library also provides an Adaptor class that allows you to adapt a Keyframed object to

In addition to the Keyframed and Looper classes, this library provides a number of utility functions and decorators that can be used to customize and extend the behavior of your keyframed objects.

For example, the frameContext decorator allows you to specify a window of keyframes around the current frame when defining a getter function. This can be useful when you want to use the values of several surrounding keyframes to calculate the value of the current frame.

The Adaptor class provides a way to transform the output of a keyframed object in a variety of ways, such as scaling, reversing, or looping. You can also use the Adaptor class to "freeze" the current state of a keyframed object by wrapping it in an adaptor and setting its freeze attribute to True.

## Conclusion

Overall, this library provides a flexible and intuitive way to create and manipulate keyframed data, making it a useful tool for a wide variety of applications. Whether you're working on a music or video project, creating animations, or just want to experiment with keyframing in general, this library is a great choice.
