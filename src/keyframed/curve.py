from abc import ABC, abstractmethod
from copy import deepcopy
from functools import reduce
from numbers import Number
import operator
from sortedcontainers import SortedDict
from typing import Tuple, Optional, Union, Dict, Callable

from .interpolation import (
    bisect_left_keyframe, 
    INTERPOLATORS,
)
from .utils import id_generator, DictValuesArithmeticFriendly


# workhorse of Curve.__init__, should probably attach it as an instance method on Curve
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
        # aaaand here we go again.
        implied_interpolation = default_interpolation
        for item in curve:
            if not isinstance(item, Keyframe):
                if len(item) == 2:
                    item = (item[0], item[1], implied_interpolation)
                item = Keyframe(*item)
            implied_interpolation = item.interpolation_method
            d_[item.t] = item
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

    def __eq__(self, other) -> bool:
       return self.value == other
    def __repr__(self) -> str:
        return f"Keyframe(t={self.t}, value={self.value}, interpolation_method='{self.interpolation_method}')"
    def _to_dict(self, *args, **kwargs) -> dict:
        return {'t':self.t, 'value':self.value, 'interpolation_method':self.interpolation_method}
    def _to_tuple(self, *args, **kwags):
        return (self.t, self.value, self.interpolation_method)
    def to_dict(self, *args, **kwags):
        return self._to_dict(*args, **kwags)
        #return self._to_tuple(*args, **kwags)

class CurveBase(ABC):
    def copy(self) -> 'CurveBase':
        return deepcopy(self)

    @property
    @abstractmethod
    def keyframes(self) -> list:
        pass

    @property
    @abstractmethod
    def values(self) -> list:
        pass
    
    @property
    @abstractmethod
    def duration(self) -> Number:
        pass 

    @abstractmethod
    def __getitem__(self) -> Number:
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
        line = plt.plot(xs, ys, *args, **kargs)
        kfx = self.keyframes
        kfy = [self[x] for x in kfx]
        plt.scatter(kfx, kfy, color=line[0].get_color())

    def random_label(self) -> str:
        return f"curve_{id_generator()}"

    def __sub__(self, other) -> 'CurveBase':
        return self + (-1 * other)

    def __rsub__(self, other) -> 'CurveBase':
        return (-1*self) + other

    def __radd__(self,other) -> 'CurveBase':
        return self+other

    def __rmul__(self, other) -> 'CurveBase':
        return self*other

    def __neg__(self) -> 'CurveBase':
        return self * (-1)

    def __eq__(self, other) -> bool:
        return self.to_dict() == other.to_dict()
    @abstractmethod
    def to_dict(simplify=False, for_yaml=False):
        raise NotImplementedError

class Curve(CurveBase):
    """
    Represents a curve as a sorted dictionary of Keyframes. Default interpolation produces a step function.

    Attributes:
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
        loop: bool = False,
        duration:Optional[float]=None,
        label:str=None,
    ):
        """
        Initializes a curve from a dictionary or another curve.

        Args:
            curve: The curve to initialize from. Can be a number, dictionary, SortedDict, or tuple of (time, value) pairs.
            loop (bool, optional): Whether the curve should loop. Defaults to False.
            duration (float, optional): The duration of the curve. Defaults to None.
        """
        if isinstance(curve, type(self)):
            self._data = curve._data
        else:
            self._data = ensure_sorteddict_of_keyframes(curve, default_interpolation=default_interpolation)

        self.default_interpolation=default_interpolation
        self.loop=loop
        self._duration=duration
        if label is None:
            label = self.random_label()
            self._using_default_label = True
        self.label=label

    @property
    def keyframes(self) -> list:
        return self._data.keys()
    
    @property
    def values(self) -> list:
        # not a fan of this
        return [kf.value for kf in self._data.values()]

    @property
    def duration(self) -> Number:
        if self._duration:
            return self._duration
        return max(self.keyframes)

    def __get_slice(self, k:slice):
        start, end = k.start, k.stop
        if (start is None) and (end is None):
            return self.copy()
        if start is None:
            start = 0
        elif start < 0:
            start = self.keyframes[start]
        if end is None:
            end = self.duration
        elif end < 0:
            end = self.keyframes[end]
        d = {}
        for k, kf in self._data.items():
            if start <= k <= end:
                d[k] = deepcopy(kf)
        for k in (start, end):
            if (k is not None) and (k not in d):
                interp = bisect_left_keyframe(k, self).interpolation_method
                kf = Keyframe(t=k, value=self[k], interpolation_method=interp)
                d[k] = kf
        # reindex to slice origin
        #d = {(k-start):kf for k,kf in d.items()}
        d2 = {}
        for k,kf in d.items():
            k_shifted = k-start
            kf.t = k_shifted
            d2[k_shifted] = kf
        d = d2

        #loop = self.loop if end# to do: revisit the logic here
        loop = False # let's just keep it like this for simplicity. if someone wants a slice output to loop, they can be explicit
        return Curve(curve=d, loop=loop, duration=end)
        
    def __getitem__(self, k:Number) -> Number:
        """
        Under the hood, the values in our SortedDict should all be Keyframe objects,
        but indexing into this class should always return a number (Keyframe.value)
        """
        if isinstance(k, slice):
            return self.__get_slice(k)

        if self.loop and k >= max(self.keyframes):
            k %= (self.duration + 1)
        if k in self._data.keys():
            outv = self._data[k]
            if isinstance(outv, Keyframe):
                outv = outv.value
            return outv

        left_value = bisect_left_keyframe(k, self)
        interp = left_value.interpolation_method

        if (interp is None) or isinstance(interp, str):
            f = INTERPOLATORS.get(interp)
            if f is None:
                raise ValueError(f"Unsupported interpolation method: {interp}")
        elif isinstance(interp, Callable):
            f = interp
        else:
            raise ValueError(f"Unsupported interpolation method: {interp}")
        
        try:
            return f(k, self)
        except IndexError:
            return left_value.value
    
    def __setitem__(self, k, v):
        if not isinstance(v, Keyframe):
            if isinstance(v, Callable):
                interp = v
                v = self[k]
            else:
                kf = bisect_left_keyframe(k,self)
                interp = kf.interpolation_method
            v = Keyframe(t=k,value=v,interpolation_method=interp)
        self._data[k] = v
    
    def __str__(self) -> str:
        d_ = {k:self[k] for k in self.keyframes}
        return f"Curve({d_}"

    def __add__(self, other) -> CurveBase:
        if isinstance(other, CurveBase):
            return self.__add_curves__(other)
        outv = self.copy()
        for k in self.keyframes:
            outv[k]= outv[k] + other
        return outv

    def __add_curves__(self, other) -> 'Composition':
        if isinstance(other, ParameterGroup):
            # this triggers the operator to get resolved by "other" instead of self
            return NotImplemented
        params = {self.label:self, other.label:other}
        new_label = '+'.join(params.keys())
        return Composition(parameters=params, label=new_label, reduction='add')

    def __mul__(self, other) -> CurveBase:
        if isinstance(other, CurveBase):
            return self.__mul_curves__(other)
        label_ = f"( {other} * {self.label} )"
        other = Curve(other)
        return Composition(parameters=(self, other), label=label_, reduction='multiply')
    
    def __mul_curves__(self, other) -> 'Composition':
        if isinstance(other, ParameterGroup):
            # this triggers the operator to get resolved by "other" instead of self
            return NotImplemented
        params = {self.label:self, other.label:other}
        new_label = '*'.join(params.keys())
        #params = ParameterGroup(params) ## added... no difference
        return Composition(parameters=params, label=new_label, reduction='multiply')

    @classmethod
    def from_function(cls, f:Callable) -> CurveBase:
        return cls({0:f(0)}, default_interpolation=lambda k, _: f(k))

    def to_dict(self, simplify=False, for_yaml=False):

        if for_yaml:
            d_curve = tuple([kf._to_tuple(simplify=simplify) for k, kf in self._data.items()])
        else:
            d_curve = {k:kf.to_dict(simplify=simplify) for k, kf in self._data.items()}
        
        # to do: make this less ugly
        if simplify:
            d_curve = {}
            recs = []
            #for t, v, kf_interp in 
            implied_interpolation = 'previous'
            for kf in self._data.values():
                if ((kf.t == 0) and (kf.value == 0) and (kf.interpolation_method == implied_interpolation)):
                    continue
                rec = {'t':kf.t,'value':kf.value}
                if kf.interpolation_method != implied_interpolation:
                    rec['interpolation_method'] = kf.interpolation_method
                    implied_interpolation = kf.interpolation_method
                if for_yaml:
                    rec = tuple(rec.values())
                    recs.append(rec)
                else:
                    t = rec.pop('t')
                    d_curve[t] = rec

            if for_yaml:
                outv = {'curve': recs}
            else:
                outv = {'curve':d_curve}

            if self.duration != kf.t: # test against timestamp of last scene keyframe 
                outv['duration'] = self.duration
            if self.loop:
                outv['loop'] = self.loop
            # uh... ignore default labels I guess? Maybe make that an option?
            if not (hasattr(self, '_using_default_label') and self.label.startswith('curve_')):
                outv['label'] = self.label
            
        else:
            outv = dict(
            curve=d_curve,
            loop=self.loop,
            duration=self.duration,
            label=self.label,
        )

        return outv


# i'd kind of like this to inherit from dict. Maybe It can inherit from DictValuesArithmeticFriendly?
class ParameterGroup(CurveBase):
    """
    The ParameterGroup class wraps a collection of named parameters to facilitate manipulating them as a unit.
    Indexing into a ParameterGroup with a frame index returns a dict giving the values of the parameters at that time.
    The returned values are scaled by a Curve attached to the ParameterGroup `weight` attribute which defaults to a constant value of 1.
    """
    def __init__(
        self,
        parameters:Union[Dict[str, Curve],'ParameterGroup', list, tuple],
        weight:Optional[Union[Curve,Number]]=1,
        label=None,
    ):
        if isinstance(parameters, list) or isinstance(parameters, tuple):
            d = {}
            for curve in parameters:
                if not isinstance(curve, CurveBase):
                    curve = Curve(curve)
                d[curve.label] = curve
            parameters = d

        if isinstance(parameters, ParameterGroup):
            pg = parameters
            self.parameters = pg.parameters
            self._weight = pg.weight
            if label is None:
                label = pg.label # to do: I think this should probably be a random label gen
            self.label = label
            return
        self.parameters = {}
        for name, v in parameters.items():
            if not isinstance(v, CurveBase):
                v = Curve(v)
            v.label = name
            self.parameters[name] = v
        if label is None:
            label = self.random_label()
            self._using_default_label = True
        self.label = label
        if not isinstance(weight, Curve):
            weight = Curve(weight)
            weight._using_default_label = True
        self._weight = weight
    
    @property
    def weight(self):
        # defining this as a property so we can override the label to 
        # always match the label of the associated ParameterGroup
        self._weight.label = f"{self.label}_WEIGHT"
        return self._weight

    def __get_slice(self, k) -> 'ParameterGroup':
        outv = self.copy()
        outv.parameters = {name:param[k] for name, param in self.parameters.items()}
        outv._weight = outv.weight[k]
        return outv

    def __getitem__(self, k) -> dict:
        if isinstance(k, slice):
            return self.__get_slice(k)
        wt = self.weight[k]
        d = {name:param[k]*wt for name, param in self.parameters.items() }
        return DictValuesArithmeticFriendly(d)

    def copy(self) -> 'ParameterGroup':
        return deepcopy(self)

    # feels a bit redundant with DictValuesArithmeticFriendly, but fuck it.
    def __add__(self, other) -> 'ParameterGroup':
        outv = self.copy()
        for k,v in outv.parameters.items():
            outv.parameters[k] = v + other
        return outv
    
    def __mul__(self, other) -> 'ParameterGroup':
        outv = self.copy()
        for k,v in outv.parameters.items():
            outv.parameters[k] = v * other
        return outv
    
    def __truediv__(self, other) -> 'ParameterGroup':
        outv = self.copy()
        for k,v in outv.parameters.items():
            outv.parameters[k] = v / other
        return outv
    
    def __rtruediv__(self, other) -> 'ParameterGroup':
        outv = self.copy()
        for k,v in outv.parameters.items():
            outv.parameters[k] = other / v
        return outv

    @property
    def duration(self) -> Number:
        return max(curve.duration for curve in self.parameters.values())

    def plot(self, n:int=None, xs:list=None, eps:float=1e-9, *args, **kargs):
        if n is None:
            n = self.duration + 1
        for curve in self.parameters.values():
            curve = curve.copy()
            curve = curve * self.weight
            curve.plot(n=n, xs=xs, eps=eps, *args, **kargs)

    @property
    def keyframes(self) -> list:
        kfs = set()
        for curve in self.parameters.values():
            kfs.update(curve.keyframes)
        kfs = list(kfs) 
        kfs.sort()
        return kfs

    @property
    def values(self) -> list:
        return [self[k] for k in self.keyframes]

    def random_label(self) -> str:
        return f"pgroup({','.join([c.label for c in self.parameters.values()])})"
    def to_dict(self, simplify=False, for_yaml=False):
        params = {k:v.to_dict(simplify=simplify, for_yaml=for_yaml) for k,v in self.parameters.items()}
        weight = self.weight.to_dict(simplify=simplify, for_yaml=for_yaml)
        
        if not simplify:
            return dict(
            parameters=params,
            weight=weight,
            label=self.label,
        )
        else:
            for k in list(params.keys()):
                if 'label' in params[k]:
                    params[k].pop('label')

            outv = {'parameters':params}
            wt2 = deepcopy(weight)
            if 'label' in wt2:
                wt2.pop('label')
            if wt2 != Curve(1).to_dict(simplify=simplify, for_yaml=for_yaml):
                outv['weight'] = wt2 #weight
            if not hasattr(self, '_using_default_label'):
                outv['label'] = self.label
            return outv

REDUCTIONS = {
    'add': operator.add,
    'sum': operator.add,
    'multiply': operator.mul,
    'product': operator.mul,
    'prod': operator.mul,
    'subtract': operator.sub,
    'sub': operator.sub,
    'divide': operator.truediv,
    'div': operator.truediv,
    'truediv': operator.truediv,
    'max':max,
    'min':min,
    ## requires special treatment by caller
    'mean': operator.add,
    'average': operator.add,
    'avg': operator.add,
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
        self.reduction = reduction
        super().__init__(parameters=parameters, weight=weight, label=label)
        # uh.... let's try this I guess?
        # uh... ok that seems to have fixed it. Interesting.
        if label is None:
            self.label = self.random_label()

    def __getitem__(self, k) -> Union[Number,dict]:
        f = REDUCTIONS.get(self.reduction)

        vals = [curve[k] for curve in self.parameters.values()]
        outv = reduce(f, vals)
        if self.reduction in ('avg', 'average', 'mean'):
            outv = outv * (1/ len(vals))
        outv = outv * self.weight[k]
        return outv

    def random_label(self, d=None) ->str:
        if d is None:
            d = self.parameters
        basename = ', '.join(d.keys())
        return f"{self.reduction}({basename})_{id_generator()}"

    def __radd__(self, other) -> 'Composition':
        return super().__radd__(other)

    def __add__(self, other) -> 'Composition':
        if not isinstance(other, CurveBase):
            other = Curve(other)

        pg_copy = self.copy()
        if self.reduction in ('sum', 'add'):
            pg_copy.parameters[other.label] = other
            return pg_copy
        else:
            d = {pg_copy.label:pg_copy, other.label:other}
            return Composition(parameters=d, weight=pg_copy.weight, reduction='sum')

    def __mul__(self, other) -> 'ParameterGroup':
        if not isinstance(other, CurveBase):
            other = Curve(other)

        pg_copy = self.copy()
        if self.reduction in ('multiply', 'mul', 'product', 'prod'):
            pg_copy.parameters[other.label] = other
            return pg_copy
        else:
            d = {pg_copy.label:pg_copy, other.label:other}
            return Composition(parameters=d, reduction='prod')

    def __truediv__(self, other) -> 'Composition':
        if not isinstance(other, CurveBase):
            other = Curve(other)

        pg_copy = self.copy()
        d = {pg_copy.label:pg_copy, other.label:other}
        return Composition(parameters=d, reduction='truediv')
    
    def __rtruediv__(self, other) -> 'Composition':
        if not isinstance(other, CurveBase):
            other = Curve(other)

        pg_copy = self.copy()
        d = {other.label:other, pg_copy.label:pg_copy} # reverse order of arguments
        return Composition(parameters=d, reduction='truediv')

    def plot(self, n:int=None, xs:list=None, eps:float=1e-9, *args, **kargs):
        """
        Arguments
            n (int): (Optional) Number of points to plot, plots range [0,n-1]. If not specified, n=self.duration.
            eps (float): (Optional) value to be subtracted from keyframe to produce additional points for plotting.
                Plotting these additional values is important for e.g. visualizing step function behavior.
        """
        is_compositional_pgroup = False
        for v in self.parameters.values():
            if isinstance(v, ParameterGroup) and not isinstance(v, Composition):
                is_compositional_pgroup = True
                break
        if not is_compositional_pgroup:
            Curve.plot(self, n=n, xs=xs, eps=eps, *args, **kargs)
        else: 
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
            # https://stackoverflow.com/questions/5558418/list-of-dicts-to-from-dict-of-lists
            ys_d =  {k: [dic[k] for dic in ys] for k in ys[0]}
            for label, values in ys_d.items():
                kargs['label'] = label
                plt.plot(xs, values, *args, **kargs)
                kfx = self.keyframes
                kfy = [self[x][label] for x in kfx]
                plt.scatter(kfx, kfy)
    def to_dict(self, simplify=False, for_yaml=False):
        outv = super().to_dict(simplify=simplify, for_yaml=for_yaml)
        outv['reduction'] = self.reduction
        return outv