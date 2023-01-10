# @title modified to use sortedcontainers
from copy import deepcopy
from sortedcontainers import SortedDict
from typing import List, Tuple, Optional, Union, Dict, Callable
from numbers import Number
#import PIL
#import torch
from loguru import logger


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


def ensure_sorteddict_of_keyframes(curve) -> SortedDict:
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
        outv = SortedDict({0:Keyframe(t=0,value=curve)})
    elif isinstance(curve, tuple):
        outv = SortedDict({k:Keyframe(t=k,value=v) for k,v in curve})
    else:
        raise NotImplementedError
    
    for k, v in list(outv.items()):
        if not isinstance(v, Keyframe):
            outv[k] = Keyframe(t=k,value=v)
    return outv




def bisect_left_value(k, K):
    """
    finds the value of the keyframe in a sorted dictionary to the left of a given key, i.e. performs "previous" interpolation
    """
    logger.debug(k)
    self=K
    right_index = self._data.bisect_right(k)
    logger.debug(right_index)
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

INTERPOLATORS={
    None:bisect_left_value,
    'previous':bisect_left_value,
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
        t,
        value,
        interpolation_method=None,
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
        logger.debug(type(other))
        logger.debug(type(self.value))
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

    Methods:
        __init__: Initializes a curve from a dictionary or another curve.
        __getitem__: Returns the value of the keyframe at a given time.
        __setitem__: Sets the value of the keyframe at a given time.
        __len__: Returns the duration of the curve.
        __str__: Returns a string representation of the curve.
    """
    def __init__(self,
        curve: Union[
            int,
            float,
            Dict,
            SortedDict,
            Tuple[Tuple[CurveKeyframe, CurveValue]],
        ] = ((0,0),),
        ease_in = None,
        ease_out = None,
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
            if ease_in is not None:
                ease_in = curve.ease_in
            if ease_out is not None:
                ease_out = curve.ease_out
        else:
            self._data = ensure_sorteddict_of_keyframes(curve)
        
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

    def __getitem__(self, k):
        if self.loop and k >= max(self.keyframes):
            k %= len(self)
        if k in self._data.keys():
            return self._data[k]
        left_value = bisect_left_value(k, self)
        logger.debug(left_value)
        f = INTERPOLATORS[left_value.interpolation_method]
        return f(k, self)
    
    def __setitem__(self, k, v):
        if not isinstance(v, Keyframe):
            if isinstance(v, Callable):
                logger.debug("callable value detected")
                interp = v
                v = None
            else:
                interp = bisect_left_value(k,self).interpolation_method
            v = Keyframe(t=k,value=v,interpolation_method=interp)
        self._data[k] = v
    
    def __str__(self):
        d_ = {k:self[k] for k in self.keyframes}
        return f"Curve({d_}"



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
    #def __getitem__(self, k) -> Union[PromptState, torch.tensor]:
    def __getitem__(self, k) -> PromptState:
        logger.debug(f"{k} {self.weight}")
        outv = PromptState(
            weight=self.weight[k],
            attribute=self.attribute,
        )
        if self.encoder is not None:
          outv = self.encoder(outv.attribute) * outv.weight
        return outv

# i'd kind of like this to inherit from dict.
class ParameterGroup:
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
        logger.debug(f"pgroup weight:{wt}")
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
    def __radd__(self,other):
        return self+other
    def __rmul__(self, other):
        return self*other
