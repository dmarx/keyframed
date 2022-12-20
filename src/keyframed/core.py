import copy
#from typing import Self # jfc colab, update your python version... python 3.11 feature
from sortedcontainers import SortedSet, SortedList

from loguru import logger
import numpy as np
from scipy.spatial import KDTree
from scipy.interpolate import interp1d
import traces

from .dsl import deforum_parse


from abc import ABC, abstractmethod
from collections.abc import Sequence

class KeyframedBase(ABC):
    def copy(self):
        return copy.deepcopy(self)

    @property
    @abstractmethod
    def keyframes(self) -> Sequence:
        pass

    @property
    @abstractmethod
    def is_bounded(self) -> bool:
        pass
    
    @abstractmethod
    def __getitem__(self, k):
        pass


class Keyframed(KeyframedBase):
    def __init__(
        self, 
        data=None, 
        interp=None, 
        default_fill_method='previous',
        n=None,
    ):
        _interp = {0:default_fill_method}
        if interp is not None:
            _interp.update(interp)
        _data={0:0}
        if data is not None:
            if isinstance(data, dict):
                _data.update(data)
            else:
                _data ={0:data}
        logger.debug(_data)
        self._d = traces.TimeSeries(_data)
        logger.debug(self._d)
        self._interp = traces.TimeSeries(_interp)
        # pre-fill memo
        self._d_memo = {k:v for k,v in _data.items() if ((not callable(v)) and (not isinstance(v, str)))}
        self.set_length(n)

    @property
    def keyframes(self):
        kf_d = [k for k,v in self._d.items()]
        kf_interp = [k for k,v in self._interp.items()]
        return SortedSet(kf_d + kf_interp)
        
    @property
    def _keyframes_memoized(self):
        """
        callables will not be evaluated. if they have been previously evaluated, those previous
        evaluations will be used
        """
        kf_d = []
        for k,v in self._d.items():
            if callable(v):
                if k not in self._d_memo:
                    continue
            kf_d.append(k)
        kf_interp = [k for k,v in self._interp.items()]
        return SortedSet(kf_d + kf_interp)

    def keyframes_neighborhood(self, k, order=2):
        """
        Returns the nearest keyframes to a given index. If the index is itself a keyframe,
        it will be included in the neighborhood.
            k: the keyframe defining the center of the neighborhood
            order: the number of neighbors to return  
        """
        rebuild = False
        keyframes = self.keyframes[:]
        if not hasattr(self, '_tree'):
            rebuild=True
        elif self._tree.n != len(keyframes):
            rebuild=True
        if rebuild:
            self._tree = KDTree(np.array([keyframes]).T)
        dd, ii = self._tree.query([k], k=order) # dd=distances, ii=indices
        return SortedList([keyframes[i] for i in ii])

    # to do: separately build left and right neighbors.
    # more flexibility for context specification, e.g. EMA vs sliding window
    # ... basically doing this already.
    def keyframe_neighbors_left(self, k, n):
        keyframes = self.keyframes
        logger.debug(keyframes)
        neighbors = []
        left_terminus = k
        while n > 0:
            logger.debug(f"order - {n} | neighbors - {neighbors}")
            left_idx = keyframes.bisect_left(left_terminus)
            try:
                left_terminus = keyframes[left_idx - 1]
            except IndexError:
                return neighbors
            logger.debug(f"left_terminus - {left_terminus} | left_idx - {left_idx}")
            if left_terminus in neighbors:
                logger.debug("left terminus in neighbors. trying again")
                left_idx = keyframes.bisect_left(left_terminus-1) # assumes unit intervals
                left_terminus = keyframes[left_idx -1]
                logger.debug(f"left_terminus - {left_terminus} | left_idx - {left_idx}")
            if not left_terminus in neighbors:
                logger.debug("left_terminus not in neighbors")
                neighbors = [left_terminus] + neighbors
                n -= 1
                logger.debug(f"neighbors - {neighbors}")
            if n <=0: break
        logger.debug(f"neighbors - {neighbors}")
        return neighbors

    def keyframe_neighbors_right(self, k, n):
        keyframes = self.keyframes
        logger.debug(keyframes)
        neighbors = []
        right_terminus = k
        while n > 0:
            logger.debug("foo0.1")
            right_idx = keyframes.bisect_right(right_terminus)
            logger.debug("foo0.2")
            try:
                right_terminus = keyframes[right_idx]
            except IndexError:
                return neighbors
            logger.debug("foo0.3")
            if right_terminus in neighbors:
                logger.debug("foo1")
                right_idx = keyframes.bisect_right(right_terminus+1) # assumes unit intervals
                logger.debug("foo2")
                right_terminus = keyframes[right_idx]
                logger.debug("foo3")
            if not right_terminus in neighbors:
                neighbors = neighbors + [right_terminus]
                n -= 1
        logger.debug(neighbors)
        return neighbors

    def keyframes_neighborhood_balanced(self, k, order=2):
        """
        Returns a neighborhood where there are as many left neighbors as right neighbors.
        Assumes order is even.
        """
        assert order % 2 == 0
        halforder = order // 2
        left_neighbors = self.keyframe_neighbors_left(k, n=halforder)
        right_neighbors = self.keyframe_neighbors_right(k, n=halforder)
        return left_neighbors + right_neighbors


    def __setitem__(self, k, v):
        """
        Assumes that we're just setting a value to the data series.
        To additionally set an accompanying value for the interpolation
        setting, use a 2-tuple for the value. To set the interpolation
        mode only, use a 2-tuple whose first value is None
        """
        interp = self._interp[k]
        if isinstance(v, tuple):
            assert len(v) == 2
            v, interp = v
        if v is not None:
            self._d[k] = v
        # let's assume that every keyframe has an associated _d value. 
        # i.e. no interpolation-only keyframes. If one is set, we infer
        # the associated value.
        else:
            v = self[k]
            self._d[k] = v
        self._interp[k] = interp # this feels like it's gonna cause problems.

    def _get_memoized(self,k):
        outv = self._pre_get(k)
        if callable(outv):
            outv = self._d_memo.get(k)
        return outv

    def _pre_get(self, k):
        # explicitly assigned values take precedence over interpolations
        if k in self._d:
            logger.debug(f"{k} in self._d")
            logger.debug(k)
            return self._d[k]
        if self.is_bounded:
            if k >= len(self):
                #raise KeyError(f"{k} is out of bounds for Keyframed of length {len(self)}")
                raise StopIteration(f"{k} is out of bounds for Keyframed of length {len(self)}")
        interp=self._interp.get(k)
        logger.debug(interp)
        if interp in ('nearest', 'nearest-up', 'zero', 'slinear', 'quadratic', 'cubic','next'):
            def _interp_func(k, K, xs, ys):
                logger.debug(xs)
                logger.debug(ys)
                f = interp1d(xs, ys, kind=interp)
                return f(k).item()
            outv = _interp_func
        else:
            outv = self._d.get(k, interpolate=interp)
        return outv

    def __getitem__(self, k):
        outv = self._pre_get(k)
        if callable(outv):
            xs_ = list(self._keyframes_memoized)
            ys_ = [self._get_memoized(i) for i in xs_]
            logger.debug((xs_,ys_))
            xs =[]
            ys = []
            for x,y in zip(xs_, ys_):
                if y is None:
                    continue
                xs.append(x)
                ys.append(y)
            success=False
            argsets = [
                [k, self, xs, ys],
                [k, self],
            ]
            for args in argsets:
                try:
                    outv = outv(*args)
                    success=True
                    break
                except TypeError:
                    continue
            if not success:
                outv = outv(k)
            self._d_memo[k] = outv
        return outv

    def __delitem__(self, k):
        self._d.pop(k, -1)
        self._interp.pop(k, -1)

    @property
    def is_bounded(self):
        if self._len is not None:
            return True
        return False

    def __len__(self):
        return self._len
    
    def set_length(self, n):
        self._len = n

    def set_unbounded(self):
        self._len = None

    # scavenged from deforum's `parse_key_frames()`
    # https://github.com/deforum/stable-diffusion/blob/c86c493bfe72640c9e95310e2ca02ad8ed7b2b97/Deforum_Stable_Diffusion.py#L1193
    @classmethod
    def from_string(cls, text, prompt_parser=None):
        frames = deforum_parse(text, prompt_parser=prompt_parser)
        # attempt to coerce string to numeric
        for k,v in list(frames.items()):
            if isinstance(v,str):
                try:
                    v=int(v)
                    frames[k]=v
                    continue
                except ValueError:
                    pass
                try:
                    v=float(v)
                    frames[k]=v
                except ValueError:
                    pass
                #try:
                #    v=ne.evaluate(v)
                #except ValueError:
                #    pass
                continue
        return cls(frames)

    #def append(self, other: Self):
    def append(self, other):
        if not self.is_bounded:
            raise RuntimeError("append operation is only supported for bounded Keyframed")
        newlen = len(self) + len(other)
        offset = len(self)
        for i, v in other._d.items():
            k = i+offset
            interp = other._interp[i]
            self._d[k] = v
            self._interp[k] = interp
        # just in case we have any interps that aren't paired with a fixed value.
        # which begs the question of whether we want that to be a thing at all.
        # maybe we can let that be a pattern for setting, but then under the hood
        # we infer the value to accompany the newly inserted interpolation mode
        for i, v in other._interp.items():
            k = i+offset
            self._interp[k] = v
        self.set_length(n=newlen)

    def __add__(self, other):
        self = copy.deepcopy(self)
        #if isinstance(other, Self):
        if isinstance(other, type(self)):
            assert self.is_bounded and other.is_bounded
            n = max(len(self), len(other))
            kf = self.keyframes
            kf.update(other.keyframes)
            for k in kf[::-1]: # iterate backwards, otherwise interpolation might cause compounding errors
                self._d[k] = self[k] + other[k]
                if any(mode=='linear' for mode in (self._interp[k], other._interp[k])):
                    self._interp[k] = 'linear'
            self.set_length(n)
        else: # assume numeric, not sure how best to assert. isinstance(other, int)?
            for k,v in self._d.items():
                self._d[k] = v + other
        return self
