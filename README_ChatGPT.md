# Keyframed

Data structures and convenience functions to facilitate working with keyframed parameters and interpolations

# ChatGPT Docs

ChatGPT generated all of the following documentation. I'm just copy-pasting it for now. then will format and edit more.

---
---

Welcome to the Keyframed library! This library is designed to allow you to specify and interpolate data at keyframes, and provide a variety of interpolation options.

In this library, a "keyframe" is a specific point in your data that has a defined value. For example, if you have a series of numbers that represent the positions of a moving object at specific times, each of those position measurements is a keyframe.

To use this library, you will first need to create a Keyframed object. You can do this by calling the Keyframed constructor and passing it either a dictionary of keyframes and their values, or a length for the data series. For example:

```python
from keyframed import Keyframed

# Create a Keyframed object with three keyframes at indices 0, 5, and 10
k = Keyframed({0: 10, 5: 20, 10: 30})

# Create a Keyframed object with a length of 20
k = Keyframed(20)
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

By default, the Keyframed object will use linear interpolation to calculate values between keyframes. However, you can specify a different interpolation method by passing it as a second argument when setting a keyframe value. For example:

```python
k = Keyframed({0: 10, 5: 20, 10: 30})
k[3] = 'quadratic'  # Use quadratic interpolation between keyframes 0 and 5

print(k[3])  # Interpolated value using quadratic interpolation
```

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




---
---

## Getting Started

Welcome to the Keyframed library! This library provides tools for working with data that has been keyframed, or organized into discrete frames at specific times.

To get started, you will first need to install the Keyframed library and its dependencies. You can do this by running the following command:

    pip install keyframed
    
Next, you can import the Keyframed class and create a new Keyframed object. The Keyframed class takes a number of optional parameters:

```python
from keyframed import Keyframed

# create a new Keyframed object with a single keyframe at time 0 and value 1
kf = Keyframed(data=1)

# create a new Keyframed object with two keyframes at times 0 and 1, with values 0 and 1 respectively
kf = Keyframed(data={0: 0, 1: 1})

# create a new Keyframed object with keyframe data specified in a dictionary, and interpolation methods specified in another dictionary
kf = Keyframed(data={0: 0, 1: 1, 2: 2}, interp={1: 'linear', 2: 'cubic'})
```

Once you have created a Keyframed object, you can access the data at a specific keyframe using the __getitem__ method:

```python
# get the data at keyframe 0
data = kf[0]
```

You can also retrieve a list of all keyframes in the Keyframed object using the keyframes property:

```python
# get a list of all keyframes
keyframes = kf.keyframes
```

You can convert the Keyframed object to have uniform keyframe spacing using the to_uniform_keyframes method:

```python
# convert the Keyframed object to have 10 keyframes with linear interpolation
kf_uniform = kf.to_uniform_keyframes(10, interp='linear')
```

That's it! You now know the basic usage of the Keyframed library. For more information, you can refer to the documentation for the full list of methods and properties available in the Keyframed class.

## Advanced Usage

Welcome to the Keyframed library! In this tutorial, we will be demonstrating advanced usage of the Keyframed library, as demonstrated in the provided test suite.

One advanced feature of the Keyframed library is the ability to use callable data getters. These are functions that can be used to compute the data at a keyframe, rather than specifying the data directly. This can be useful when the data at a keyframe depends on the data at other keyframes, or when the data needs to be computed using a specific algorithm.

To use a callable data getter, you can assign the function to a keyframe using the `__setitem__` method:

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
```

Another advanced feature of the Keyframed library is the ability to specify interpolation methods for the data. This can be useful when the data is not available at all keyframes, and needs to be interpolated in order to be evaluated at other keyframes. The Keyframed library provides several interpolation methods, including linear, quadratic, and cubic.

To specify an interpolation method for a keyframe, you can use the interp parameter of the Keyframed class:

```python
# create a new Keyframed object with three keyframes, using quadratic interpolation for the data at keyframe 2
kf = Keyframed(data={0: 0, 1: 1, 3: 9}, interp={2: 'quadratic'})

# the data at keyframe 2 should now be interpol
```

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

Finally, the Keyframed library also provides tools for converting a Keyframed object to have uniform keyframe spacing. This can be useful when you need to work with data that has been keyframed at irregular intervals, and you want to resample the data at a fixed interval. To convert a Keyframed object to have uniform keyframe spacing, you can use the to_uniform_keyframes method:

```python
# create a new Keyframed object with some initial data
kf = Keyframed(data={0: 0, 1: 1, 3: 2, 5: 2, 6: 2, 8: 1})

# convert the Keyframed object to have 10 keyframes with linear interpolation
kf_uniform = kf.to_uniform_keyframes(10, interp='linear')
```

That's it! You now know the advanced usage of the Keyframed library, as demonstrated in the provided test suite. For more information, you can refer to the documentation for the full list of methods and properties available in the Keyframed class.




# Keyframed: A Time Series Data Type

Keyframed is a time series data type that allows users to store and retrieve data at specified time indices. It is built on top of the traces library, which provides a data structure for storing time series data and a set of functions for manipulating that data.

## Installation

To install Keyframed, use pip:

    pip install keyframed

## Basic Usage

To create a new Keyframed object, you can pass in a dictionary of data where the keys are time indices and the values are the data at those indices. You can also specify a length for the time series, which will set the bounds for indexing. If no length is specified, the time series will be unbounded.

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

# returns 1
print(k[0])

# returns the data at the nearest keyframe before the index (1)
print(k[5])

# returns the data at the nearest keyframe after the index (2)
print(k[15])
```

## Keyframes and Interpolation

A keyframe is a time index with data stored at it. You can retrieve the set of keyframes for a Keyframed object using the keyframes property.

```python
k = Keyframed({0: 1, 10: 2})

# returns {0, 10}
print(k.keyframes)
```

You can specify an interpolation method for data at indices between keyframes by passing a dictionary of interpolation methods to the interp argument when creating a Keyframed object. The keys of the dictionary are time indices and the values are the interpolation methods to use at those indices.

```python
k = Keyframed({0: 1, 10: 2}, interp={5: 'linear'})

# returns the data at the nearest keyframe before the index (1)
print(k[2])

# returns the linearly interpolated data between keyframes 0 and 10
print(k[5])

# returns the data at the nearest keyframe after the index (2)
print(k[15])
```

## Appending Time Series

You can append two Keyframed objects by using the append method. This will concatenate the two time series and adjust the keyframes and interpolation methods accordingly.

```python
k1 = Keyframed({0: 1, 10: 2})
k2 = Keyframed({20: 3, 30: 4})

k1.append(k2)

# returns {0,
```

To use the Keyframed class in this library, you can create an instance of the class with a given set of data points, or you can initialize an empty instance and set data points later. You can set the length of the Keyframed object, which will cause it to behave like a bounded sequence. Alternatively, you can leave the length unset, which will allow the Keyframed object to behave like an unbounded sequence.

You can access the data points of a Keyframed object by indexing it like a sequence. If the index you specify is not a keyframe (i.e., a data point that has been explicitly set), the value will be interpolated based on the surrounding keyframes. The default method of interpolation is "previous", which will simply return the value of the closest preceding keyframe. However, you can specify a different method of interpolation when setting a keyframe, or you can specify a callable function that will be used to generate the value at the given index.

You can append one Keyframed object to another using the append method. This will add the data points and keyframes of the second object to the end of the first object, and will adjust the length of the first object accordingly.

You can also modify the keyframes and data points of a Keyframed object by setting new values using the indexing syntax. This will create a new keyframe at the specified index, with the given value and interpolation method. If you want to specify a different interpolation method than the default, you can pass a tuple containing the value and the interpolation method as the value when setting a keyframe.

Finally, you can use the copy method to create a deep copy of the Keyframed object. This can be useful if you want to make changes to a Keyframed object without affecting the original.

Here is some more detailed information about the Keyframed class and its methods:

```
Keyframed(data=None, interp=None, default_fill_method='previous', n=None) -> None
This is the constructor for the Keyframed class. It takes the following optional arguments:

data: a dictionary mapping indices to data values. This can be used to specify the keyframes and data points for the Keyframed object.
interp: a dictionary mapping indices to interpolation methods. This can be used to specify the interpolation method for a given index. If a value is not given for a particular index, the default interpolation method (specified by default_fill_method) will be used.
default_fill_method: the default interpolation method to use when a value is not specified in the interp dictionary. The default value is "previous".
n: the length of the Keyframed object. If this is set, the object will behave like a bounded sequence. If it is not set (None), the object will behave like an unbounded sequence.
copy() -> 'Keyframed'
This method creates a deep copy of the Keyframed object. The copy will have its own data points and keyframes, and will not be affected by any changes made to the original object.

keyframes
This is a read-only property that returns a sorted set of the indices that are keyframes in the Keyframed object.

is_bounded
This is a read-only property that returns True if the Keyframed object has a length (i.e., it is bounded) and False otherwise.

__getitem__(self, k)
This method allows you to access the data point at a given index by using the indexing syntax (e.g., k[10]). If the index is a keyframe, the value of the keyframe will be returned. If the
```


## Basic Concepts

Here are some basic concepts related to the Keyframed class:

### Keyframes

A keyframe is an index in the Keyframed object that has a specific data value associated with it. Keyframes can be specified when creating a Keyframed object using the data argument in the constructor, or they can be added later using the indexing syntax (e.g., k[10] = 3). Keyframes can be accessed directly by indexing the Keyframed object (e.g., k[10]).

### Keyframed

When a data value is associated with a specific index in a Keyframed object, that index is considered a "keyframe". The term "keyframed" refers to the process of specifying data values for specific indices in a Keyframed object.

### Boundedness

A Keyframed object can be either bounded or unbounded. A bounded Keyframed object has a fixed length, meaning that it can only store data points up to a certain index. An unbounded Keyframed object does not have a fixed length, and can store data points at any index. The boundedness of a Keyframed object is determined by the n argument in the constructor.

### Interpolation

Interpolation is the process of estimating a value between two known values based on their relative positions. The Keyframed class allows you to specify an interpolation method for a given index, which will be used to estimate the value of that index based on the values of



# Introduction to Looping Keyframed Objects

The Looper class allows you to create an iterable that repeats a Keyframed object a certain number of times, with optional activation and deactivation points. This is useful for creating looping patterns such as LFOs (low-frequency oscillators).

## Basic Concepts

To use Looper, you will first need to understand a few basic concepts:

* Keyframes: In a Keyframed object, keyframes are specific indices where a value is defined. All other indices are filled in using interpolation.

* Keyframing: Keyframing refers to the process of defining specific values at keyframes and using interpolation to fill in values for the indices in between.

* Boundedness: A Keyframed object is said to be bounded if it has a defined length. An unbounded Keyframed object has no defined length and can be iterated indefinitely.

* Interpolation: Interpolation is the process of estimating a value between two known values. In the context of a Keyframed object, interpolation is used to estimate the values for indices between keyframes.

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

# Advanced Usage

You can also use the Adaptor class to wrap a Keyframed object and

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

Examples


## Intro tutorial

Welcome to the keyframed library! This library provides a powerful and flexible way to represent sequences of values that can change over time. The core concept in this library is the "keyframe", which is a point in time where the value of the sequence is explicitly defined. Keyframes can be used to specify the values of a sequence at specific points in time, and the library will automatically interpolate (estimate) the values of the sequence at all other points in time based on the keyframes.

To use the keyframed library, you will first need to create a Keyframed object. You can do this by calling the Keyframed constructor and passing it a dictionary of keyframes. For example:

```python
from keyframed import Keyframed

k = Keyframed({0: 0, 5: 5, 10: 10})
```

This creates a Keyframed object with three keyframes at times 0, 5, and 10, with corresponding values of 0, 5, and 10. You can then access the values of the sequence at any point in time by indexing the Keyframed object with a time. For example:

```python
print(k[0])  # prints 0
print(k[5])  # prints 5
print(k[10]) # prints 10
print(k[2.5]) # prints 2.5
print(k[7.5]) # prints 7.5
```

By default, the Keyframed object will interpolate the values of the sequence using a linear interpolation. You can specify a different interpolation method by passing a dictionary of interpolation methods to the interp parameter of the Keyframed constructor. For example:

```python
k = Keyframed({0: 0, 5: 5, 10: 10}, interp={5: 'previous'})
```

This creates a Keyframed object with the same keyframes as before, but with a different interpolation method at time 5. Specifically, the interpolation method at time 5 is set to "previous", which means that the value of the sequence at time 5 will be equal to the value of the sequence at the previous keyframe (in this case, time 0).

You can also specify a custom interpolation function by passing a callable (a function or a method) to the interp parameter. The callable should accept three arguments: the current time, the Keyframed object, and a tuple of arrays of times and values for the surrounding keyframes. For example:

```python
from scipy.interpolate import interp1d

def quadratic_interp(k, K, xs, ys):
    f = interp1d(xs, ys, kind='quadratic')
    return f(k).item()

k = Keyframed({0: 0, 5: 5, 10: 10}, interp={5: quadratic_interp})
```

This creates a Keyframed object with the same keyframes as before, but with a quadratic interpolation at time 5.

In addition to interpolating the values of the sequence, the Keyframed library also provides several other features and functionality, such as the ability to append two Keyframed objects together, loop a Keyframed object over a fixed number of repetitions, and resolve a
