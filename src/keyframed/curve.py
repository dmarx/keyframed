# @title modified to use sortedcontainers
from copy import deepcopy
from sortedcontainers import SortedDict
from typing import List, Tuple, Optional, Union, Dict, Callable
from numbers import Number
#import PIL
#import torch
#from loguru import logger


try:
    from typing import TypeAlias
    
    #PromptAttribute: TypeAlias = Union[str, PIL.Image.Image]
    PromptAttribute: TypeAlias = str
    CurveKeyframe: TypeAlias = Number
    CurveValue: TypeAlias = Number
except ImportError:
    #PromptAttribute = Union[str, PIL.Image.Image]
    PromptAttribute = str
    CurveKeyframe = Number
    CurveValue = Number


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

def scipy_interp(k:Number, curve:'Curve', kind:str, **kargs) -> Callable:
    """
    Wraps scipy.interpolate.interp1d for use with Curve objects.
    """
    from scipy.interpolate import interp1d
    left = bisect_left_keyframe(k, curve)
    right = bisect_right_keyframe(k, curve)
    xs = [left.t, right.t]
    ys = [left.value, right.value]
    #t = (xs[0]-k)/(xs[1]-xs[0])
    f = interp1d(x=xs, y=ys, kind=kind, **kargs)
    #return f(t)
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
    def __add__(self, other):
        if isinstance(other, type(self)):
            other = other.value
        return self.value + other
    def __radd__(self,other):
        return self+other
    def __le__(self, other):
        if isinstance(other, type(self)):
            other = other.value
        return self.value <= other
    def __ge__(self, other):
        if isinstance(other, type(self)):
            other = other.value
        return self.value >= other
    def __lt__(self, other):
        if isinstance(other, type(self)):
            other = other.value
        return self.value < other
    def __gt__(self, other):
        if isinstance(other, type(self)):
            other = other.value
        return self.value > other
    def __mul__(self, other):
        if isinstance(other, type(self)):
            other = other.value
        return self.value * other
    def __rmul__(self, other):
        return self*other
    def __eq__(self, other) -> bool:
        return self.value == other
    def __repr__(self):
        return f"Keyframe(t={self.t}, value={self.value}, interpolation_method='{self.interpolation_method}')"


class EasingFunction:
    def __init__(self, f:Callable=None, curve:'Curve'=None, start_t:Number=None, end_t:Number=None):
        if f is None:
            f = lambda x: x
        self.f = f
        self.curve=curve
        self._start_t=start_t
        self._end_t=end_t
    @property
    def start_t(self):
        start_t = self._start_t
        if start_t is None:
            start_t = self.get_ease_start_t()
        return start_t
    @property
    def end_t(self):
        end_t = self._end_t
        if end_t is None:
            end_t = self.get_ease_end_t()
        return end_t
    def get_ease_start_t(self):
        return 0
    def get_ease_end_t(self):
        return 0
    def use_easing(self, k):
        return self.start_t < k < self.end_t 
    def __call__(self,k):
        if not self.use_easing(k):
            return k
        span = self.end_t - self.start_t
        #t = (k-self.start_t) / span
        t = (self.end_t-k) / span
        t_new = self.f(t)
        k_new = self.start_t + t_new*span
        return k_new


class EaseIn(EasingFunction):
    def get_ease_start_t(self):
        if not self.curve:
            return 0
        #return 0
        k_prev = 0
        for k in self.curve.keyframes:
            if self.curve[k] != 0:
                return k_prev
            k_prev = k
    def get_ease_end_t(self):
        #return self.curve.keyframes[1]
        for k in self.curve.keyframes:
            if self.curve[k] != 0:
                return k


class EaseOut(EasingFunction):
    def get_ease_start_t(self):
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
    def get_ease_end_t(self):
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
            Tuple[Tuple[CurveKeyframe, CurveValue]],
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

    # fuck... should this return a Keyframe or a number? probably a number.
    def __getitem__(self, k):
        if self.loop and k >= max(self.keyframes):
            k %= len(self)
        if k in self._data.keys():
            return self._data[k]

        left_value = bisect_left_keyframe(k, self)
        interp = left_value.interpolation_method

        if self.ease_in.use_easing(k):
            k = self.ease_in(k)
        elif self.ease_out.use_easing(k):
            k = self.ease_out(k)

        if (interp is None) or isinstance(interp, str):
            f = INTERPOLATORS.get(interp)
            if f is None:
                f = scipy_interp(k, self, kind=interp)
                return f(k)
        elif isinstance(interp, Callable):
            f = interp
        else:
            raise NotImplementedError(f"Unsupported interpolation method: {interp}")
        return f(k, self)
    
    def __setitem__(self, k, v):
        if not isinstance(v, Keyframe):
            if isinstance(v, Callable):
                interp = v
                #v = None
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

    def __add__(self, other):
        if isinstance(other, type(self)):
            return self.__add_curves__(other)
        outv = self.copy()
        for k in self.keyframes:
            outv[k]+=other
        return outv

    def __add_curves__(self, other):
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

    def __mul__(self, other):
        outv = self.copy()
        for i, k in enumerate(self.keyframes):
            kf = outv[k]
            kf.value = kf.value * other
            outv[k]=kf
        return outv
    def __rmul__(self, other):
        return self*other


# can probably just use Keyframe for the return value
class PromptState:
    """
    this class basically exists for the __mul__ method, which I just needed to
    facilitate respecting the weight of the containing ParameterGroup
    """
    def __init__(self, weight, attribute):
        assert weight is not None
        assert attribute is not None
        self.weight = weight
        self.attribute=attribute
    def __mul__(self, other):
        return PromptState(
            weight = self.weight*other, 
            attribute =self.attribute)
    def __repr__(self):
        return f"PromptState(weight={self.weight},attribute={self.attribute})"


class Prompt:
    def __init__(
        self, 
        attribute: PromptAttribute, # want this to support arbitrary attributes, but keeping these two mainly in mind
        weight: Optional[Union[Curve, Number]] = 1,
        encoder:Optional[Callable]=None,
    ):
        """
        Attribute: The prompt text, image, etc.
        """
        self.attribute=attribute
        self.encoder = encoder
        if not isinstance(weight, Curve):
            weight = Curve(weight)
        self.weight=weight
        if encoder is not None:
            self._attribute_encoded = encoder(self.attribute)
    #def __getitem__(self, k) -> Union[PromptState, torch.tensor]:
    def __getitem__(self, k) -> PromptState:
        wt = self.weight[k]
        val = self.attribute
        if hasattr(self, '_attribute_encoded'):
            val = self._attribute_encoded
            return wt*val
        if isinstance(val, Number):
            return wt*val
        return PromptState(
            weight=wt,
            attribute=val,
        )


# i'd kind of like this to inherit from dict.
class ParameterGroup:
    """
    The ParameterGroup class represents a set of parameters that can be applied to a prompt.
    It is initialized with a dictionary of parameters, where the keys are the names of the parameters and the values are either Curve objects or Prompt objects.
    It also has an optional weight parameter, which is a Curve or a Number that is used to modulate the values of the parameters.
    The class provides a magic method for getting the current parameter values at a given key, and also provides magic methods for addition and multiplication,
    allowing for easy modification of the weight parameter. It also has a copy method for creating a deep copy of itself.
    """
    def __init__(
        self,
        parameters:Dict[float, Union[Curve,Prompt]]=None,
        weight:Optional[Union[Curve,Number]]=1
    ):
        if not isinstance(weight, Curve):
            weight = Curve(weight)
        self.weight = weight
        self.parameters={}
        for name, v in parameters.items():
            if isinstance(v, int) or isinstance(v, float):
                v = Curve(v)
            #if isinstance(v, str) or isinstance(v, PIL.Image.Image):
            #    v = Prompt(v)
            self.parameters[name] = v

    def __getitem__(self, k):
        wt = self.weight[k]
        return {name:param[k]*wt for name, param in self.parameters.items() }

    # this might cause performance issues down the line. deal with it later.
    def copy(self):
        return deepcopy(self)

    def __add__(self, other):
        outv = self.copy()
        outv.weight = outv.weight + other
        return outv

    def __mul__(self, other):
        outv = self.copy()
        outv.weight = outv.weight * other
        return outv

    def __radd__(self,other):
        return self+other

    def __rmul__(self, other):
        return self*other
