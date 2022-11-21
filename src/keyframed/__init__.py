import copy
import traces
from operator import add
from infinity import inf
#from typing import Self # jfc colab, update your python version... python 3.11 feature
from sortedcontainers import SortedSet, SortedList
import re

from scipy.spatial import KDTree
from scipy.interpolate import interp1d
import numexpr as ne
import numpy as np

from loguru import logger

def deforum_parse(string, prompt_parser=None):
    # because math functions (i.e. sin(t)) can utilize brackets 
    # it extracts the value in form of some stuff
    # which has previously been enclosed with brackets and
    # with a comma or end of line existing after the closing one
    pattern = r'((?P<frame>[0-9]+):[\s]*\((?P<param>[\S\s]*?)\)([,][\s]?|[\s]?$))'
    frames = dict()
    for match_object in re.finditer(pattern, string):
        frame = int(match_object.groupdict()['frame'])
        param = match_object.groupdict()['param']
        if prompt_parser:
            frames[frame] = prompt_parser(param)
        else:
            frames[frame] = param
    if frames == {} and len(string) != 0:
        raise RuntimeError('Key Frame string not correctly formatted')
    return frames


def to_keyframed(curve, n=None):
    """
    dummy-proof coersion
    """
    if isinstance(curve, Keyframed):
        k = curve
    elif isinstance(curve, str):
        k = Keyframed.from_string(curve)
    elif isinstance(curve, dict):
        k = Keyframed(curve)
    if n:
        k.set_length(n)
    return k


class Keyframed:
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
        self._d = traces.TimeSeries(_data)
        self._interp = traces.TimeSeries(_interp)
        self._d_memo = {}
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
                #v = self._d_memo[k]
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


    def keyframes_neighborhood_balanced(self, k, order=2):
        """
        Returns a neighborhood where there are as many left neighbors as right neighbors.
        If the an odd `order` is given, the left candidate will be preferred.
        """
        keyframes = self.keyframes
        logger.debug(keyframes)
        neighbors = []
        left_terminus = right_terminus = k
        while order > 0:
            logger.debug(f"order - {order} | neighbors - {neighbors}")
            left_idx = keyframes.bisect_left(left_terminus)
            left_terminus = keyframes[left_idx - 1]
            logger.debug(f"left_terminus - {left_terminus} | left_idx - {left_idx}")
            if left_terminus in neighbors:
                logger.debug("left terminus in neighbors. trying again")
                left_idx = keyframes.bisect_left(left_terminus-1) # assumes unit intervals
                left_terminus = keyframes[left_idx -1]
                logger.debug(f"left_terminus - {left_terminus} | left_idx - {left_idx}")
            if not left_terminus in neighbors:
                logger.debug("left_terminus not in neighbors")
                neighbors = [left_terminus] + neighbors
                order -= 1
                logger.debug(f"neighbors - {neighbors}")
            if order <=0: break
            ###################
            right_idx = keyframes.bisect_right(right_terminus)
            right_terminus = keyframes[right_idx]
            if right_terminus in neighbors:
                right_idx = keyframes.bisect_right(right_terminus+1) # assumes unit intervals
                right_terminus = keyframes[right_idx]
            if not right_terminus in neighbors:
                neighbors = neighbors + [right_terminus]
                order -= 1
        return neighbors

    # def polynomial_interp(self, k, order=2):
    #     xs = self.keyframes_neighborhood_balanced(k, order)
    #     ys = [self[x] for x in xs]
    #     interpkind=[None, 'linear','quadratic','cubic']
    #     f = interp1d(xs, ys, kind=interpkind[order])
    #     return f(k)

    def copy(self):
        return copy.deepcopy(self)

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
        if self.is_bounded:
            if k >= len(self):
                #raise KeyError(f"{k} is out of bounds for Keyframed of length {len(self)}")
                raise StopIteration(f"{k} is out of bounds for Keyframed of length {len(self)}")
        interp=self._interp.get(k)
        outv = self._d.get(k, interpolate=interp)
        if callable(outv):
            return self._d_memo.get(k)

    def __getitem__(self, k):
        if self.is_bounded:
            if k >= len(self):
                #raise KeyError(f"{k} is out of bounds for Keyframed of length {len(self)}")
                raise StopIteration(f"{k} is out of bounds for Keyframed of length {len(self)}")
        interp=self._interp.get(k)
        outv = self._d.get(k, interpolate=interp)
        if callable(outv):
            xs = list(self._keyframes_memoized)
            ys = [self._get_memoized(i) for i in xs]
            success=False
            argsets = [
                [k, self, xs, ys],
                [k, self],
                #[k],
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
