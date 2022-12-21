# Keyframed: A Time Series Data Type

Keyframed is a time series data type that allows users to store and retrieve data at specified time indices. It is built on top of the `traces` library, which provides a data structure for storing time series data and a set of functions for manipulating that data.

*(Fun fact: basically all of this documentation was generated by ChatGPT! I'm still editing it down some, WIP)*

## Summary

The main purpose of this library is to implement the `Keyframed` class, which can be initialized with a set of data points or a single datum, and the length of the object can be set to create a bounded sequence or left unset to create an unbounded sequence. "Keyframes" are specific indices where a value is defined, and interpolation is used to estimate values for indices between keyframes. 

You can access the data points of a Keyframed object by indexing it like a sequence. If the index you specify is not a keyframe (i.e., a data point that has been explicitly set), the value will be interpolated based on the surrounding keyframes. The default method of interpolation is "previous", which will simply return the value of the closest preceding keyframe. However, you can specify a different method of interpolation when setting a keyframe, or you can specify a callable function that will be used to generate the value at the given index. To access a list of indices which are considered keyframes, use the `.keyframes` method. Keyframed objects can be iterated over and support basic arithmetic operations.

The motivation of this library is to facilitate object-oriented parameterization of generative animations, specifically working towards a replacement for the keyframing DSL developed by Chigozie Nri for parameterizing AI art animations (i.e. the keyframing syntax used by tools such as Disco Diffusion and Deforum).

## Installation

To install Keyframed, use pip:

    pip install keyframed
    
## Getting Started
    
To use the Keyframed class, you can create an instance of the class with a given set of data points, or you can provide a single datum which will be reused for all keyframes. You can set the length of the Keyframed object, which will cause it to behave like a bounded sequence. Alternatively, you can leave the length unset, which will allow the Keyframed object to behave like an unbounded sequence.


```python
from keyframed import Keyframed

# create a new Keyframed object with a single keyframe at time 0 with value 1
kf = Keyframed(data=1)

# create a new Keyframed object with two keyframes at times 0 and 1, with values 0 and 1 respectively
kf = Keyframed(data={0: 0, 1: 1})

# create a new Keyframed object with keyframe data specified in a dictionary, and interpolation methods specified in another dictionary
kf = Keyframed(data={0: 0, 1: 1, 2: 2}, interp={1: 'linear', 2: 'cubic'})
```

## Basic Concepts

- **Keyframe**: In a Keyframed object, keyframes are specific indices where a value is defined. All other indices are filled in using interpolation.

- **Keyframing**: Keyframing refers to the process of defining specific values at keyframes and using interpolation to fill in values for the indices in between.

- **Boundedness**: A Keyframed object is said to be bounded if it has a defined length. An unbounded Keyframed object has no defined length and can be iterated indefinitely.

- **Interpolation**: Interpolation is the process of estimating a value between two known values. In the context of a Keyframed object, interpolation is used to estimate the values for indices between keyframes.

## Basic Usage

In this library, a "keyframe" is a specific point in your data that has a defined value. For example, if you have a series of numbers that represent the positions of a moving object at specific times, each of those position measurements is a keyframe.

To create a new Keyframed object, you can pass in a dictionary of data where the keys are time indices and the values are the data at those indices. You can also specify a length for the time series, which will set the bounds for indexing. If no length is specified, the time series will be unbounded.

By default, Keyframed objects are unbounded and can be iterated indefinitely. However, you can also create a bounded Keyframed object by setting the `n` parameter when creating the object. 

```python
from keyframed import Keyframed

# create a Keyframed object with data at time indices 0 and 10
k = Keyframed({0: 1, 10: 2})

# create a Keyframed object with data at time indices 0 and 10 and a length of 20
k = Keyframed({0: 1, 10: 2}, n=20)
```

You can retrieve the data at a specific time index using the indexing operator ([]). If the index is not a keyframe (a time index with data stored at it), the data at the nearest keyframe will be interpolated. The default interpolation method is "previous," which returns the data at the nearest keyframe before the index.

```python
k = Keyframed({0: 1, 10: 2})

# The value at this index was set explicitly above
print(k[0]) # 1

# Uses the default 'previous' interpolation method to return the data at the nearest keyframe before the requested index
print(k[5]) # 1
print(k[15]) # 2
```

You can also set the value at a keyframe by using the square bracket operator with assignment, just like a dict:

```python
k = Keyframed({0: 10, 5: 20, 10: 30})
k[15] = 40

print(k[15])  # 40
```

You can retrieve and modify the keyframes and data points of a Keyframed object by setting new values using the indexing syntax. This will create a new keyframe at the specified index, with the given value and interpolation method. If you want to specify a different interpolation method than the default, you can pass a tuple containing the value and the interpolation method as the value when setting a keyframe.

## Keyframes and Interpolation

A keyframe is a time index with data stored at it. You can retrieve the set of keyframes for a Keyframed object using the keyframes property.


To get a list of all indices at which a data value has been concretely set and/or at which an interpolation method has been specified, access the `.keyframes` property:

```python
k = Keyframed({0: 1, 10: 2})

# returns {0, 10}
print(k.keyframes)
```

You can specify an interpolation method for data at indices between keyframes by passing a dictionary of interpolation methods to the `interp` argument when creating a `Keyframed` object. The keys of the dictionary are time indices and the values are the interpolation methods to use starting at those indices. Specification of interpolation method follows "previous" rules.

```python
k = Keyframed({0: 1, 10: 2}, interp={5: 'linear'})

# returns the data at the nearest keyframe before the index (1)
print(k[2])

# returns the linearly interpolated data between keyframes 4 (1) and 10 (2)
print(k[5]) # 1.1666

# returns the data at the nearest keyframe after the index (2)
print(k[15])
```

You can also set or change the interpolation method at any time by setting an index to a tuple of `(value, interpolation method)`.

```python
k[3] = 1, 'linear'
```

To set an interpolation method without specifying the series value at that index, use `None` for the value.

```python
k[3] = None, 'linear'
```

Time indices at which an interpolation method has been specified are considered keyframes, whether or not a specific data value has also been set at that time index.

```python
k = Keyframed({0: 1, 10: 2}, interp={5: 'linear'})
k[3] = None, 'linear'
k.keyframes # [0, 3, 5, 10]
```

## Appending

You can append one Keyframed object to another using the append method. This will concatenate the data points and keyframes of the second object to the end of the first object, and will adjust the length of the first object accordingly.

```python
k1 = Keyframed({0: 1, 10: 2}, n=30)
k2 = Keyframed({20: 3, 30: 4}, n=40)

k3 = k1.append(k2) # Keyframed({0:1, 10:2, 50:3, 60:4})
len(k3) == len(k1) + len(k2) == 70
```

## Copying

Finally, you can use the copy method to create a deep copy of the Keyframed object. This can be useful if you want to make changes to a Keyframed object without affecting the original.

```python
k1 = Keyframed({0: 1, 10: 2}, n=30)
k2 = k1.copy()
```


## Interpolation


By default, the Keyframed object will use `previous` interpolation to calculate values between keyframes, i.e. it will check the value for the previous frame and use that to fill the current frame. All interpolation methods supported by the 'kind' argument of [`scipy.interpolate.interp1d`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html) are supported out-of-the box, just ask for them by name. These include linear, quadratic, and cubic interpolation, as well as a number of other options.


To specify an interpolation method for a keyframe, you can use the interp parameter of the Keyframed class:

```python
# create a new Keyframed object with three keyframes, using quadratic interpolation for the data at keyframe 2
kf = Keyframed(data={0: 0, 1: 1, 3: 9}, interp={2: 'quadratic'})

kf[2] # 4
```

# Advanced Usage

## Using Callables

You can specify a callable function as the value for a keyframe. This function should generally take two positional arguments: the index of the keyframe being accessed and the Keyframed object itself. The function can then use the values of other keyframes to calculate the value for the keyframe being accessed. For example:

```python
# define a callable data getter that computes the next value in the Fibonacci sequence
def fib_get(k, K):
    return K[k-1] + K[k-2]

# create a new Keyframed object with two initial values in the Fibonacci sequence
fib_seq = Keyframed({0: 1, 1: 1})

# use the callable data getter to compute the next value in the sequence
fib_seq[2] = fib_get

# the data at keyframe 2 should now be the sum of the data at keyframes 0 and 1
assert fib_seq[2] == 2

# The default 'previous' interpolation broadcasts the fib_get function forward
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

# Looper

## Introduction to Looping Keyframed Objects

The Looper class allows you to create an iterable that repeats a Keyframed object a certain number of times, with optional activation and deactivation points. This is useful for creating looping patterns such as LFOs (low-frequency oscillators).

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

# The Looper object returns 0 values until time index 5, at which point it becomes active and begins reading from the keyframed sequence
# it was initiatlized with
print(looper[0])  # Output: 0
print(looper[5])  # Output: 0
print(looper[10])  # Output: 10

# the sequence restarts
print(looper[11])  # Output: 0
print(looper[12])  # Output: 1

# and continues for 5 repatitions before deactivating
print(looper[30])  # Output: 10
print(looper[31])  # Output: 0
print(looper[32])  # Output: 0
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



## Adaptor

In addition to the Keyframed and Looper classes, the Keyframed library also provides an Adaptor class that allows you to adapt a Keyframed object to

In addition to the Keyframed and Looper classes, this library provides a number of utility functions and decorators that can be used to customize and extend the behavior of your keyframed objects.

For example, the frameContext decorator allows you to specify a window of keyframes around the current frame when defining a getter function. This can be useful when you want to use the values of several surrounding keyframes to calculate the value of the current frame.

The Adaptor class provides a way to transform the output of a keyframed object in a variety of ways, such as scaling, reversing, or looping. You can also use the Adaptor class to "freeze" the current state of a keyframed object by wrapping it in an adaptor and setting its freeze attribute to True.

## Conclusion

Overall, this library provides a flexible and intuitive way to create and manipulate keyframed data, making it a useful tool for a wide variety of applications. Whether you're working on a music or video project, creating animations, or just want to experiment with keyframing in general, this library is a great choice.
