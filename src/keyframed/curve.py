# @title modified to use sortedcontainers

from sortedcontainers import SortedDict
import copy
from dataclasses import dataclass
import datetime as dt
import abc
from typing import List, Tuple, Optional, Union, Dict, Callable
from functools import lru_cache
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


def ensure_sorteddict_of_keyframes(curve):
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
    INTERPOLATORS[name] = f


class Keyframe:
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
        return f"Keyframe(t={self.t}, value={self.value}, interpolation_method={self.interpolation_method})"


class Curve:
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

    @lru_cache
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
    facilitate respecting the 'visibility' weight of the containing ParameterGroup
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

