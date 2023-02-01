from abc import ABC, abstractmethod
from copy import deepcopy
from functools import reduce
import math
from numbers import Number
from sortedcontainers import SortedDict
from typing import List, Tuple, Optional, Union, Dict, Callable


def ensure_sorteddict_of_keyframes(curve: 'Curve',default_interpolation:Union[str,Callable]='previous') -> SortedDict:
    """
    - If the input curve is already a sorted dictionary, it is returned as is.
    - If it is a regular dictionary, it is coerced to a sorted dictionary.
    - If it is a number, a sorted dictionary with one keyframe at t=0 is returned.
    - If it is a tuple, it is assumed to be in the format ((k0,v0), (k1,v1), ...).
    """
    if isinstance(curve, SortedDict):
        sorteddict = curve
    elif isinstance(curve, dict):
        sorteddict = SortedDict(curve)
    elif isinstance(curve, Number):
        sorteddict = SortedDict({0:Keyframe(t=0,value=curve, interpolation_method=default_interpolation)})
    elif (isinstance(curve, list) or isinstance(curve, tuple)):
        d_ = {}
        for item in curve:
            if isinstance(item, Keyframe):
                d_[item.t] = item
            else:
                k,v = item
                d_[k] = v
        sorteddict = SortedDict(d_)
    else:
        raise NotImplementedError

    d_ = {}
    implied_interpolation = default_interpolation
    if 0 not in sorteddict:
        d_[0] = Keyframe(t=0,value=0, interpolation_method=implied_interpolation)
    for k,v in sorteddict.items():
        if isinstance(v, Keyframe):
            implied_interpolation = v.interpolation_method
            d_[k] = v
        elif isinstance(v, dict):
            kf = Keyframe(**v)
            if 'interpolation_method' not in v:
                kf.interpolation_method = implied_interpolation
            implied_interpolation = kf.interpolation_method
            if k != kf.t:
                kf.t = k
            d_[k] = kf
        elif isinstance(v, list) or isinstance(v, tuple):
            kf = Keyframe(*v)
            if len(v) < 3:
                kf.interpolation_method = implied_interpolation
            implied_interpolation = kf.interpolation_method
            d_[k] = kf
        elif isinstance(v, Number):
            d_[k] = Keyframe(t=k,value=v, interpolation_method=implied_interpolation)
        else:
            raise NotImplementedError
    return SortedDict(d_)


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
# ... increasingly unsure how I feel about this, as implemented at least.
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
        try:
            start = self.start_t
            end = self.end_t
        except IndexError:
            return False
        if (start is None) or (end is None):
            return False
        return start < k < end
    def __call__(self,k:Number) -> Number:
        if not self.use_easing(k):
            return k
        span = self.end_t - self.start_t
        t = (k-self.start_t) / span
        #t = (self.end_t-k) / span
        t_new = self.f(t)
        k_new = self.start_t + t_new*span
        return k_new


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


class CurveBase(ABC):
    def copy(self):
        return deepcopy(self)

    @property
    @abstractmethod
    def keyframes(self):
        pass

    @property
    @abstractmethod
    def values(self):
        pass
    
    @property
    @abstractmethod
    def duration(self):
        pass 

    @abstractmethod
    def __getitem__(self):
        pass

    def plot(self, n:int=None, xs:list=None, eps:float=1e-9, *args, **kargs):
        """
        Arguments
            n (int): (Optional) Number of points to plot, plots range [0,n-1]. If not specified, n=self.duration.
            eps (float): (Optional) value to be subtracted from keyframe to produce additional points for plotting.
                Plotting these additional values is important for e.g. visualizing step function behavior.
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError("Please install matplotlib to use Curve.plot()")
        if xs is None:
            if n is None:
                n = self.duration + 1
            xs_base = list(range(int(n))) + list(self.keyframes)
            xs = set()
            for x in xs_base:
                if (x>0) and (eps is not None) and (eps > 0):
                    xs.add(x-eps)
                xs.add(x)
        xs = list(set(xs))
        xs.sort()
        
        ys = [self[x] for x in xs]
        if kargs.get('label') is None:
            kargs['label']=self.label
        plt.plot(xs, ys, *args, **kargs)
        kfx = self.keyframes
        kfy = [self[x] for x in kfx]
        plt.scatter(kfx, kfy)


class Curve(CurveBase):
    """
    Represents a curve as a sorted dictionary of Keyframes. Default interpolation produces a step function.

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
        label:str=None,
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
        self.label=label

    @property
    def keyframes(self):
        return self._data.keys()
    
    @property
    def values(self):
        # not a fan of this
        return [kf.value for kf in self._data.values()]

    @property
    def duration(self):
        if self._duration:
            return self._duration
        #return max(self.keyframes)+1
        return max(self.keyframes)

    def __getitem__(self, k:Number) -> Number:
        """
        Under the hood, the values in our SortedDict should all be Keyframe objects,
        but indexing into this class should always return a number (Keyframe.value)
        """
        if self.loop and k >= max(self.keyframes):
            k %= (self.duration + 1)
        if k in self._data.keys():
            outv = self._data[k]
            if isinstance(outv, Keyframe):
                outv = outv.value
            return outv
        #if k > self.duration:
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

    def __add__(self, other) -> CurveBase:
        if isinstance(other, CurveBase):
            return self.__add_curves__(other)
        outv = self.copy()
        for k in self.keyframes:
            outv[k]+=other
        return outv

    def __to_labeled(self, other) -> dict:
        self_label = self.label
        if self_label is None:
            self_label = 'this'
        other_label = other.label
        if other_label is None:
            other_label = 'that'
        if self_label == other_label:
            other_label += '1'
        return {self_label:self, other_label:other}

    def __add_curves__(self, other) -> 'Composition':
        params = self.__to_labeled(other)
        new_label = '+'.join(params.keys())
        return Composition(parameters=params, label=new_label, reduction='add')

    def __mul__(self, other) -> CurveBase:
        if isinstance(other, CurveBase):
            return self.__mul_curves__(other)
        outv = self.copy()
        for i, k in enumerate(self.keyframes):
            kf = outv._data[k]
            kf.value = kf.value * other
            outv[k]=kf
        return outv
    
    def __mul_curves__(self, other) -> 'Composition':
        params = self.__to_labeled(other)
        pg = ParameterGroup(params)
        new_label = '*'.join(params.keys())
        return Composition(parameters=pg, label=new_label, reduction='multiply')

    def __rmul__(self, other) -> 'Curve':
        return self*other


def SmoothCurve(*args, **kargs):
    """
    Thin wrapper around the Curve class that uses an 'eased_lerp' for `default_interpolation` to produce a smooth curve
    instead of a step function. In the future, the interpolation function on this class may be modified to use a different
    smoothing interpolator.
    """
    return Curve(*args, default_interpolation='eased_lerp', **kargs)


# i'd kind of like this to inherit from dict.
class ParameterGroup(CurveBase):
    """
    The ParameterGroup class wraps a collection of named parameters to facilitate manipulating them as a unit.
    Indexing into a ParameterGroup with a frame index returns a dict giving the values of the parameters at that time.
    The returned values are scaled by a Curve attached to the ParameterGroup `weight` attribute which defaults to a constant value of 1.
    """
    def __init__(
        self,
        parameters:Union[Dict[str, Curve],'ParameterGroup'],
        weight:Optional[Union[Curve,Number]]=1
    ):
        if isinstance(parameters, ParameterGroup):
            pg = parameters
            self.parameters = pg.parameters
            self.weight = pg.weight
            return
        if not isinstance(weight, Curve):
            weight = Curve(weight)
        self.weight = weight
        self.parameters={}
        for name, v in parameters.items():
            if not isinstance(v, CurveBase):
                v = Curve(v)
            v.label = name
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

    @property
    def duration(self):
            return max(curve.duration for curve in self.parameters.values())

    def plot(self):
        n = self.duration + 1
        for curve in self.parameters.values():
            curve.plot(n=n)

    @property
    def keyframes(self):
        kfs = set()
        for curve in self.parameters.values():
            kfs.update(curve.keyframes)
        kfs = list(kfs) 
        kfs.sort()
        return kfs

    @property
    def values(self):
        return [self[k] for k in self.keyframes]


REDUCTIONS = {
    'add':lambda x,y:x+y,
    'multiply':lambda x,y:x*y,
    'subtract':lambda x,y:x-y,
    'divide':lambda x,y:x/y,
}


class Composition(ParameterGroup):
    """
    Synthesizes a new curve by performing a reduction operation over two or more
    other curves. The value for a given keyframe k is computed by evaluating the
    input curves at k, then performing the reduction operation over the resultant values.
    The input curves are assumed to be passed by reference, so modifications to the
    input Curve objects will propogate to compositions of those curves.

    Arguments
      parameters (ParameterGroup): The curves to be composed, encapsulated in a ParameterGroup
      reduction (Callable): A function that defines the combination operator.
      label (str): Optional label, e.g. for plotting. If not provided, one will be inferred from the parameters.
    """
    def __init__(
        self,
        parameters:Union[Dict[str, Curve],'ParameterGroup'],
        weight:Optional[Union[Curve,Number]]=1,
        reduction:str=None,
        label:str=None,
    ):
        super().__init__(parameters=parameters, weight=weight)
        self.reduction = reduction
        self._label=label
    def __getitem__(self, k):
        f = REDUCTIONS.get(self.reduction)
        vals = super().__getitem__(k).values()
        outv = reduce(f, vals)
        return outv
    @property
    def _default_label(self):
        return ''.join([f"({k})" for k in self.parameters.keys()])
    @property
    def label(self):
        if self._label is not None:
            return self._label
        return self._default_label
