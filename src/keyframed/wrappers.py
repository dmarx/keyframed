from loguru import logger
from keyframed.core import Keyframed, KeyframedBase
from collections.abc import Sequence
from abc import ABC, abstractmethod


class Adaptor(KeyframedBase):
    _inactive_value=0
    """
    Adds an interface layer that converts an external "global" timestep to an "internal" timestep,
    which permits things like resetting the local timestep after the global timestep is greater than the duration
    of the internal timestep, or dilating/contracting internal steps relative to global to create a slowdown/speedup effect
    """
    def __init__(
        self, 
        K, 
        inactive_value=None,
    ):
        self._seq = K
        if inactive_value is None:
            self.inactive_value = self._inactive_value

    @abstractmethod
    def external_step_to_internal_step(self, t_ext):
        pass

    def is_active(self, k):
        if not self.is_bounded:
            return True
        else:
            return k < len(self)

    def inactive_behavior(self):
        return self.inactive_value
    def __getitem__(self, k):
        if self.is_active(k):
            k = self.external_step_to_internal_step(k)
            return self._seq[k]
        else:
            return self.inactive_behavior()


class Looper(Adaptor):
    """
    Turns a fixed length Keyframed into a repeating loop. repeats can be parameterized by:
    - number of repeats
    - duration of 'super-sequence'
    """
    def __init__(
        self,
        K:Keyframed,
        activate_at=0,
        deactivate_after=None,
        max_repetitions=None,
    ):
        # looping only makes sense if K is fixed length
        #assert K.is_bounded
        # If provided an unbounded sequence, assume that the last keyframe sets the upper bound.
        if not K.is_bounded:
            K=K.copy()
            K.set_length(max(K.keyframes)+1)
        super().__init__(K)
        self.activate_at=activate_at
        self.deactivate_after=deactivate_after
        self.max_repetitions=max_repetitions
    
    @property
    def keyframes(self) -> Sequence:
        K = self.resolve()
        return K.keyframes

    @property
    def is_bounded(self):
        return (self.deactivate_after is not None) or (self.max_repetitions is not None)
    def __len__(self):
        if not self.is_bounded:
            raise ValueError("Unbounded Sequence has no valid __len__ attribute")
        n = None
        if self.deactivate_after is not None:
            n = self.deactivate_after - self.activate_at
        if self.max_repetitions is not None:
            n2 = self.max_repetitions * len(self._seq)
            if n is None:
                n = n2
            n = min(n, n2)
        if n is None:
            raise RuntimeError(
                "Sequence is bounded but but an isue was encountered cpomp[uting length. "
                "You should never see this message. Please file an issue reporting the circumstances "
                "which caused this message to arise: httpsL//github.com/dmarx/keyframed/issues/new"
            )
        return n

    def is_active_at(self, k):
        is_active = False
        if k >= self.activate_at:
            is_active = True
        if self.deactivate_after is not None:
            if k > self.deactivate_after:
                is_active = False
        if self.max_repetitions is not None:
            max_k = self.max_repetitions * len(self._seq) + self.activate_at
            if k > max_k:
                is_active = False
        return is_active

    def external_step_to_internal_step(self, k):
        k -= self.activate_at
        return k % len(self._seq)
    
    def resolve(self, keyframes_only=False):
        if keyframes_only:
            raise NotImplementedError
        assert self.is_bounded
        d_ = {k:self._seq[k] for k in range(len(self))}
        return Keyframed(d_, n=len(self))

