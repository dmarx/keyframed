import pytest

from keyframed import Keyframed
from keyframed.wrappers import Adaptor, Looper

def test_init_adaptation():
    K = Keyframed()
    A = Adaptor(K)

def test_init_loop():
    K = Keyframed()
    K.set_length(1)
    L = Looper(K)

# def test_loop_bounded():
#     K = Keyframed()
#     with pytest.raises(AssertionError):
#         L = Looper(K)

def test_loop_autobounded():
    K = Keyframed({0:1, 9:10}, interp={0:'linear'})
    L = Looper(K)
    assert len(L._seq) == 10

def test_loop_sawtooth_inf():
    K = Keyframed({0:1, 9:10}, interp={0:'linear'},n=10)
    L = Looper(K)
    assert K[0] == L[0] == L[10] == 1
    assert K[9] == L[9] == L[19] == 10
    assert K[4] == L[4] == L[14] == 5

def test_loop_active_bounded():
    K = Keyframed({0:1, 4:10})
    L = Looper(K, max_repetitions=5, activate_at=5)
    assert L.is_bounded
    assert len(L) == 25
    assert L.is_active_at(5)
    assert L.is_active_at(25)
    assert L.is_active_at(30)
    assert not L.is_active_at(0)
    assert not L.is_active_at(4)
    assert not L.is_active_at(31)

def test_loop_active_unbounded():
    pass

def test_loop_length_maxreps():
    K = Keyframed({0:1, 4:10})
    L = Looper(K, max_repetitions=5, activate_at=5)
    assert L.is_bounded
    assert len(L) == 25

def test_loop_length_deativated():
    pass

