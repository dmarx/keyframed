from copy import deepcopy
from sortedcontainers import SortedDict
from typing import List, Tuple, Optional, Union, Dict, Callable
from numbers import Number


def ensure_sorteddict_of_keyframes(curve: 'Curve',default_interpolation:Union[str,Callable]='previous') -> SortedDict:
    """
    - If the input curve is already a sorted dictionary, it is returned as is.
    - If it is a regular dictionary, it is coerced to a sorted dictionary.
    - If it is a number, a sorted dictionary with one keyframe at t=0 is returned.
    - If it is a tuple, it is assumed to be in the format ((k0,v0), (k1,v1), ...).
    """
    if isinstance(curve, SortedDict):
        outv = curve
    elif isinstance(curve, dict):
        outv = SortedDict(curve)
    elif isinstance(curve, Number):
        outv = SortedDict({0:Keyframe(t=0,value=curve, interpolation_method=default_interpolation)})
    elif isinstance(curve, tuple):
        outv = SortedDict({k:Keyframe(t=k,value=v, interpolation_method=default_interpolation) for k,v in curve})
    else:
        raise NotImplementedError
    if 0 not in outv:
        outv[0] = 0
    for k, v in list(outv.items()):
        if not isinstance(v, Keyframe):
            outv[k] = Keyframe(t=k,value=v, interpolation_method=default_interpolation)
    return outv


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

# NB: interp1d only supports INTERPOLATION, not extrapolation.
def scipy_interp(k:Number, curve:'Curve', kind:str, **kargs) -> Callable:
    """
    Wraps scipy.interpolate.interp1d for use with Curve objects.
    """
    from scipy.interpolate import interp1d
    left = bisect_left_keyframe(k, curve)
    right = bisect_right_keyframe(k, curve)
    xs = [left.t, right.t]
    ys = [left.value, right.value]
    f = interp1d(x=xs, y=ys, kind=kind, **kargs)
    return f

INTERPOLATORS={
    None:bisect_left_value,
    'previous':bisect_left_value,
    'next':bisect_right_value,
}

def register_interpolation_method(name:str, f:Callable):
    """
    Adds a new interpolation method to the INTERPOLATORS registry.
    """
    INTERPOLATORS[name] = f


class Keyframe:
    """
    Represents a single keyframe in a curve. Comes with magic methods to support arithmetic operations on the value attribute.
    """
    def __init__(
        self,
        t:Number,
        value,
        interpolation_method:Optional[Union[str,Callable]]=None,
    ):
        self.t=t
        self.value=value
        self.interpolation_method=interpolation_method
    @classmethod
    def _to_value(cls, other:Union['Keyframe', Number]):
        """
        Convenience function for working with objects that could either be a Keyframe or a Number
        """
        if isinstance(other, cls):
            other = other.value
        if not isinstance(other, Number):
            raise TypeError
        return other

    def __add__(self, other) -> Number:
        return self.value + self._to_value(other)
    def __radd__(self,other) -> Number:
        return self+other
    def __le__(self, other) -> bool:
        return self.value <= self._to_value(other)
    def __ge__(self, other) -> bool:
        return self.value >= self._to_value(other)
    def __lt__(self, other) -> bool:
        return self.value < self._to_value(other)
    def __gt__(self, other) -> bool:
        return self.value > self._to_value(other)
    def __mul__(self, other) -> Number:
        return self.value * self._to_value(other)
    def __rmul__(self, other) -> Number:
        return self*other
    def __eq__(self, other) -> bool:
        return self.value == other
    def __repr__(self) -> str:
        return f"Keyframe(t={self.t}, value={self.value}, interpolation_method='{self.interpolation_method}')"


class EasingFunction:
    def __init__(self, f:Callable=None, curve:'Curve'=None, start_t:Number=None, end_t:Number=None):
        #if f is None:
        #    f = lambda x: x
        self.f = f
        self.curve=curve
        self._start_t=start_t
        self._end_t=end_t
    @property
    def start_t(self) -> Number:
        start_t = self._start_t
        if start_t is None:
            start_t = self.get_ease_start_t()
        return start_t
    @property
    def end_t(self) -> Number:
        end_t = self._end_t
        if end_t is None:
            end_t = self.get_ease_end_t()
        return end_t
    def get_ease_start_t(self) -> Number:
        return 0
    def get_ease_end_t(self) -> Number:
        return 0
    def use_easing(self, k) -> bool:
        if self.f is None:
            return False
        return self.start_t < k < self.end_t 


# NB: It's worrisome to me that I had to separately implement __call__ for EaseIn and EaseOut
#     rather than just using a shared __call__ implementation on EasingFunction. I think I inverted
#     some stuff in EaseOut maybe?

class EaseIn(EasingFunction):
    def get_ease_start_t(self) -> Number:
        if not self.curve:
            return 0
        k_prev = 0
        for k in self.curve.keyframes:
            if self.curve[k] != 0:
                return k_prev
            k_prev = k
    def get_ease_end_t(self) -> Number:
        for k in self.curve.keyframes:
            if self.curve[k] != 0:
                return k
    def __call__(self,k:Number) -> Number:
        if not self.use_easing(k):
            return k
        span = self.end_t - self.start_t
        t = (k-self.start_t) / span
        #t = (self.end_t-k) / span
        t_new = self.f(t)
        k_new = self.start_t + t_new*span
        return k_new

class EaseOut(EasingFunction):
    def get_ease_start_t(self) -> Number:
        #return self.curve.keyframes[-2]
        k_prev = -1
        for k in list(self.curve.keyframes)[::-1]:
            if k_prev < 0:
                k_prev = k
                continue
            if self.curve[k] != self.curve[k_prev]:
                return k
            k_prev = k
        else:
            return self.curve.keyframes[-2]
    def get_ease_end_t(self) -> Number:
        #return self.curve.keyframes[-1]
        k_prev = -1
        for k in list(self.curve.keyframes)[::-1]:
            if k_prev < 0:
                k_prev = k
                continue
            if self.curve[k] != self.curve[k_prev]:
                return k_prev
            k_prev = k
        else:
            return self.curve.keyframes[-1]
    def __call__(self,k:Number) -> Number:
        if not self.use_easing(k):
            return k
        span = self.end_t - self.start_t
        #t = (k-self.start_t) / span
        t = (self.end_t-k) / span
        t_new = self.f(t)
        k_new = self.start_t + t_new*span
        return k_new

class Curve:
    """
    Represents a curve as a sorted dictionary of Keyframes.

    Attributes:
        ease_in (str): The method used for easing in to the curve.
        ease_out (str): The method used for easing out of the curve.
        loop (bool): Whether the curve should loop.

    Properties:
        keyframes: Returns an iterator over the times of the keyframes in the curve.
        values: Returns an iterator over the values of the keyframes in the curve.
    """
    def __init__(self,
        curve: Union[
            int,
            float,
            Dict,
            SortedDict,
            Tuple[Tuple[Number, Number]],
        ] = ((0,0),),
        default_interpolation='previous',
        ease_in:Union[EaseIn, Callable] = None,
        ease_out:Union[EaseOut, Callable] = None,
        loop: bool = False,
        duration:Optional[float]=None,
    ):
        """
        Initializes a curve from a dictionary or another curve.

        Args:
            curve: The curve to initialize from. Can be a number, dictionary, SortedDict, or tuple of (time, value) pairs.
            ease_in (str, optional): [NotImplemented] The method used for easing in to the curve. Defaults to None.
            ease_out (str, optional): [NotImplemented] The method used for easing out of the curve. Defaults to None.
            loop (bool, optional): Whether the curve should loop. Defaults to False.
            duration (float, optional): The duration of the curve. Defaults to None.
        """
        if isinstance(curve, type(self)):
            self._data = curve._data
            # process overrides if present
            #.... actually, is this the override priority i want?
            if ease_in is not None:
                ease_in = curve.ease_in
            if ease_out is not None:
                ease_out = curve.ease_out
        else:
            self._data = ensure_sorteddict_of_keyframes(curve, default_interpolation=default_interpolation)

        self.default_interpolation=default_interpolation
        if not isinstance(ease_in, EasingFunction):
            ease_in = EaseIn(f=ease_in, curve=self)
        else:
            ease_in.curve=self
        if not isinstance(ease_out, EasingFunction):
            ease_out = EaseOut(f=ease_out, curve=self)
        else:
            ease_out.curve=self

        self.ease_in=ease_in
        self.ease_out=ease_out
        self.loop=loop
        self._duration=duration
        
    @property
    def keyframes(self):
        return self._data.keys()
    
    @property
    def values(self):
        # not a fan of this
        return [kf.value for kf in self._data.values()]

    def __len__(self):
        if self._duration:
            return self._duration
        return max(self.keyframes)+1

    def __getitem__(self, k:Number) -> Number:
        """
        Under the hood, the values in our SortedDict should all be Keyframe objects,
        but indexing into this class should always return a number (Keyframe.value)
        """
        if self.loop and k >= max(self.keyframes):
            k %= len(self)
        if k in self._data.keys():
            outv = self._data[k]
            if isinstance(outv, Keyframe):
                outv = outv.value
            return outv
        #if k > (len(self)-1):
        #    return 0

        left_value = bisect_left_keyframe(k, self)
        interp = left_value.interpolation_method

        if self.ease_in.use_easing(k):
            k = self.ease_in(k)
        elif self.ease_out.use_easing(k):
            k = self.ease_out(k)

        try:
            if (interp is None) or isinstance(interp, str):
                f = INTERPOLATORS.get(interp)
                if f is None:
                    f = scipy_interp(k, self, kind=interp)
                    #f = INTERPOLATORS[None]
                    return f(k)
            elif isinstance(interp, Callable):
                f = interp
            else:
                raise NotImplementedError(f"Unsupported interpolation method: {interp}")
            return f(k, self)
        # Fallback for issues encountered from calling bisect_right_keyframe inside scipy_interp
        except IndexError:
            #return 0
            return left_value.value
    
    def __setitem__(self, k, v):
        if not isinstance(v, Keyframe):
            if isinstance(v, Callable):
                interp = v
                v = self[k]
            else:
                # should we use self.default_interpolation here?
                kf = bisect_left_keyframe(k,self)
                interp = kf.interpolation_method
            v = Keyframe(t=k,value=v,interpolation_method=interp)
        self._data[k] = v
    
    def __str__(self):
        d_ = {k:self[k] for k in self.keyframes}
        return f"Curve({d_}"

    ##########################
    def copy(self):
        return deepcopy(self)

    def __add__(self, other) -> 'Curve':
        if isinstance(other, type(self)):
            return self.__add_curves__(other)
        outv = self.copy()
        for k in self.keyframes:
            outv[k]+=other
        return outv

    def __add_curves__(self, other) -> 'Curve':
        outv = self.copy()
        other = other.copy()

        # step 1. lift current keyframes by what `other` evaluates to at that point
        for k in outv.keyframes:
            outv._data[k].value = self[k] + other[k]

        # step 2. perform the converse operation on `other` using what `self` evaluates to at its keyframes
        for k in other.keyframes:
            other[k] += self[k]

        # step 3. for any keys which `other` has but `self` does not, pop that item from `other` and insert it into `outv`.
        for k, kf in other._data.items():
            if k not in outv.keyframes:
                outv._data[k] = kf
        
        return outv

    def __mul__(self, other) -> 'Curve':
        outv = self.copy()
        for i, k in enumerate(self.keyframes):
            kf = outv._data[k]
            kf.value = kf.value * other
            outv[k]=kf
        return outv
    def __rmul__(self, other) -> 'Curve':
        return self*other


# i'd kind of like this to inherit from dict.
class ParameterGroup:
    """
    The ParameterGroup class wraps a collection of named parameters to facilitate manipulating them as a unit.
    Indexing into a ParameterGroup with a frame index returns a dict giving the values of the parameters at that time.
    The returned values are scaled by a Curve attached to the ParameterGroup `weight` attribute which defaults to a constant value of 1.
    """
    def __init__(
        self,
        parameters:Dict[str, Curve],
        weight:Optional[Union[Curve,Number]]=1
    ):
        if not isinstance(weight, Curve):
            weight = Curve(weight)
        self.weight = weight
        self.parameters={}
        for name, v in parameters.items():
            if isinstance(v, Number):
                v = Curve(v)
            self.parameters[name] = v

    def __getitem__(self, k) -> dict:
        wt = self.weight[k]
        return {name:param[k]*wt for name, param in self.parameters.items() }

    # this might cause performance issues down the line. deal with it later.
    def copy(self) -> 'ParameterGroup':
        return deepcopy(self)

    def __add__(self, other) -> 'ParameterGroup':
        outv = self.copy()
        outv.weight = outv.weight + other
        return outv

    def __mul__(self, other) -> 'ParameterGroup':
        outv = self.copy()
        outv.weight = outv.weight * other
        return outv

    def __radd__(self,other) -> 'ParameterGroup':
        return self+other

    def __rmul__(self, other) -> 'ParameterGroup':
        return self*other
