import math
from numbers import Number
from typing import Callable


def bisect_left_keyframe(k: Number, curve:'Curve') -> 'Keyframe':
    """
    finds the value of the keyframe in a sorted dictionary to the left of a given key, i.e. performs "previous" interpolation
    """
    self=curve
    right_index = self._data.bisect_right(k)
    left_index = right_index - 1
    if right_index > 0:
        _, left_value = self._data.peekitem(left_index)
    else:
        raise RuntimeError(
            "The return value of bisect_right should always be greater than zero, "
            f"however self._data.bisect_right({k}) returned {right_index}."
            "You should never see this error. Please report the circumstances to the library issue tracker on github."
            )
    return left_value

def bisect_left_value(k: Number, curve:'Curve') -> 'Keyframe':
    kf = bisect_left_keyframe(k, curve)
    return kf.value

def bisect_right_keyframe(k:Number, curve:'Curve') -> 'Keyframe':
    """
    finds the value of the keyframe in a sorted dictionary to the right of a given key, i.e. performs "next" interpolation
    """
    self=curve
    right_index = self._data.bisect_right(k)
    if right_index > 0:
        _, right_value = self._data.peekitem(right_index)
    else:
        raise RuntimeError(
            "The return value of bisect_right should always be greater than zero, "
            f"however self._data.bisect_right({k}) returned {right_index}."
            "You should never see this error. Please report the circumstances to the library issue tracker on github."
            )
    return right_value

def bisect_right_value(k: Number, curve:'Curve') -> 'Keyframe':
    kf = bisect_right_keyframe(k, curve)
    return kf.value

def sin2(t:Number) -> Number:
    return (math.sin(t * math.pi / 2)) ** 2

# to do: turn this into a decorator in dmarx/Keyframed
def eased_lerp(k:Number, curve:'Curve', ease:Callable=sin2) -> Number:
    left = bisect_left_keyframe(k, curve)
    right = bisect_right_keyframe(k, curve)
    xs = [left.t, right.t]
    ys = [left.value, right.value]

    span = xs[1]-xs[0]
    t = (k-xs[0]) / span
    t_new = ease(t)
    return ys[1] * t_new + ys[0] * (1-t_new)

def linear(k, curve):
    left = bisect_left_keyframe(k, curve)
    right = bisect_right_keyframe(k, curve)
    x0, x1 = left.t, right.t
    y0, y1 = left.value, right.value
    d = x1-x0
    t = (x1-k)/d
    outv =  t*y0 + (1-t)*y1
    return outv

INTERPOLATORS={
    None:bisect_left_value,
    'previous':bisect_left_value,
    'next':bisect_right_value,
    'eased_lerp':eased_lerp,
    'linear':linear,
}

def register_interpolation_method(name:str, f:Callable):
    """
    Adds a new interpolation method to the INTERPOLATORS registry.
    """
    INTERPOLATORS[name] = f

def get_context_left(k, curve, n, eps=1e-9):
  kfs = []
  while len(kfs) < n:
    k = bisect_left_keyframe(k, curve).t
    kfs.append(k)
    if k == 0:
      break
    k -= eps
  return kfs

def get_context_right(k, curve, n, eps=1e-9):
  kfs = []
  while len(kfs) < n:
    k = bisect_right_keyframe(k, curve).t
    kfs.append(k)
    if k == 0:
      break
    k += eps
  return kfs