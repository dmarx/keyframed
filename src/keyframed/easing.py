"""
Probably gonna remove all of this anyway. moving it here for now
to at least reduce clutter.
"""

from numbers import Number
from typing import Callable


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
