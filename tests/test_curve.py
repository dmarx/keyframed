from keyframed import Curve, Prompt, ParameterGroup, register_interpolation_method, Keyframe
from keyframed.curve import ensure_sorteddict_of_keyframes, bisect_left_value, INTERPOLATORS

def test_curve():
    c = Curve()

def test_prompt():
    p = Prompt("foo bar")

def test_param_group():
    c = Curve(((0,0), (1,1)))
    p = Prompt("foo bar", weight=1.5)
    settings = ParameterGroup({
        'curve':c,
        'prompt':p,
        'scalar':10,
    })
    print(settings[0])
    print(settings[1])
    print(settings[2])
    settings.visibility = Curve(((2,.5),))
    print(settings[2])

def test_curve_looping():
    curve = Curve(((0, 0), (9, 9)), loop=True)
    for i in range(20):
      print(f"{i}:{curve[i]}")
    assert curve[0] == 0
    assert curve[9] == 9
    assert curve[15] == 0
    assert curve[19] == 9

#########################

# scavenged from test_callable_patterns.py


TEST_EPS = 1e-8

Keyframed = Curve

# implement fibonnaci
def test_fib():
    def fib_get(k, K):
        return K[k-1]+K[k-2]
    #fib_seq = Keyframed({0:1,1:1})
    #fib_seq[2] = fib_get
    register_interpolation_method('fib_get', fib_get)
    fib_seq = Keyframed({0:Keyframe(t=0, value=1, interpolation_method='fib_get')})
    fib_seq[1]=1
    assert fib_seq[0] == 1
    assert fib_seq[1] == 1
    assert fib_seq[2] == 2
    assert fib_seq[3] == 3
    assert fib_seq[4] == 5
    assert fib_seq[8] == 34

def test_fib_jump():
    def fib_get(k, K):
        return K[k-1]+K[k-2]
    register_interpolation_method('fib_get', fib_get)
    fib_seq = Keyframed({0:Keyframe(t=0, value=1, interpolation_method='fib_get')})
    fib_seq[1]=1
    assert fib_seq[8] == 34

from scipy.interpolate import interp1d

def test_quad_explicit():
    seq={0:0,1:1,3:9,4:16}
    K = Keyframed(seq)
    def quad_interp(k, K):
        xs = list(K.keyframes)
        ys = list(K.values)
        f = interp1d(xs, ys, kind='quadratic')
        return f(k).item()
    #K[2]=quad_interp
    register_interpolation_method('quad_interp', quad_interp)
    K[1] = Keyframe(t=1, value=1, interpolation_method='quad_interp')
    print(K[2])
    assert 4-TEST_EPS <= K[2] <= 4+TEST_EPS

###############################

# lazy chatgpt tests

import pytest

from sortedcontainers import SortedDict

def test_ensure_sorteddict_of_keyframes():
    # Test input that is already a sorted dictionary
    curve = SortedDict({0:0, 1:1})
    assert ensure_sorteddict_of_keyframes(curve) == curve
    
    # Test input that is a regular dictionary
    curve = {0:0, 1:1}
    assert ensure_sorteddict_of_keyframes(curve) == SortedDict(curve)
    
    # Test input that is a number
    curve = 0
    assert ensure_sorteddict_of_keyframes(curve) == SortedDict({0:Keyframe(t=0,value=curve)})
    
    # Test input that is a tuple
    curve = ((0,0), (1,1))
    assert ensure_sorteddict_of_keyframes(curve) == SortedDict({k:Keyframe(t=k,value=v) for k,v in curve})
    
    # Test input that is not a sorted dictionary, dictionary, number, or tuple
    curve = [0,1]
    with pytest.raises(NotImplementedError):
        ensure_sorteddict_of_keyframes(curve)

def test_bisect_left_value():
    # Test input that is in the sorted dictionary
    K = Curve(curve={0:0, 1:1})
    assert bisect_left_value(0, K) == 0
    assert bisect_left_value(1, K) == 1
    
    # Test input that is not in the sorted dictionary
    K = Curve(curve={0:0, 1:1})
    assert bisect_left_value(0.5, K) == 0
    
    # Test input that is before the start of the sorted dictionary
    K = Curve(curve={0:0, 1:1})
    with pytest.raises(RuntimeError):
        bisect_left_value(-1, K)

def test_register_interpolation_method():
    def my_interp(k, K):
        return 0
    register_interpolation_method('my_interp', my_interp)
    assert INTERPOLATORS['my_interp'] == my_interp

def test_Keyframe():
    # Test addition
    kf1 = Keyframe(t=0, value=0)
    kf2 = Keyframe(t=0, value=1)
    assert (kf1 + kf2) == 1
    assert (kf1 + 1) == 1
    assert (1 + kf1) == 1
    
    # Test comparison
    kf1 = Keyframe(t=0, value=0)
    kf2 = Keyframe(t=0, value=1)
    assert kf1 <= kf2
    assert kf1 < kf2
    assert kf2 >= kf1

    # Test arithmetic operations
    kf1 = Keyframe(t=0, value=0)
    kf2 = Keyframe(t=1, value=1)
    assert (kf1 + kf2) == 1
    assert (kf1 + 1) == 1
    assert (1 + kf1) == 1
    assert (kf1 * kf2) == 0
    assert (kf1 * 2) == 0
    assert (2 * kf1) == 0
    assert (kf1 <= kf2) == True
    assert (kf1 <= 1) == True
    assert (1 <= kf1) == False
    assert (kf1 >= kf2) == False
    assert (kf1 >= 1) == False
    assert (1 >= kf1) == True
    assert (kf1 < kf2) == True
    assert (kf1 < 1) == True
    assert (1 < kf1) == False
    assert (kf1 > kf2) == False
    assert (kf1 > 1) == False
    assert (1 > kf1) == True
    assert (kf1 == kf2) == False
    assert (kf1 == 1) == False
    assert (1 == kf1) == False
    
    # Test equality and string representation
    kf1 = Keyframe(t=0, value=0, interpolation_method='previous')
    kf2 = Keyframe(t=0, value=0, interpolation_method='previous')
    kf3 = Keyframe(t=1, value=0, interpolation_method='previous')
    assert kf1 == kf2
    assert kf1 == kf3 # whether or not this SHOULD evaluate to true is a different question. ChatGPT disagress with me.
    assert str(kf1) == "Keyframe(t=0, value=0, interpolation_method='previous')"

def test_curve():
    # Test basic curve construction
    curve1 = Curve()
    assert len(curve1) == 1
    assert list(curve1.keyframes) == [0]
    assert list(curve1.values) == [0]
    
    curve2 = Curve(duration=5)
    assert len(curve2) == 5
    assert list(curve2.keyframes) == [0]
    assert list(curve2.values) == [0]
    
    curve3 = Curve(((0,0), (2,2)))
    assert len(curve3) == 3
    assert list(curve3.keyframes) == [0, 2]
    assert list(curve3.values) == [0, 2]
    
    curve4 = Curve({0:0, 2:2})
    assert len(curve4) == 3
    assert list(curve4.keyframes) == [0, 2]
    assert list(curve4.values) == [0, 2]
    
    # Test looping behavior
    curve5 = Curve(duration=5, loop=True)
    assert curve5[5] == curve5[0]
    
    # Test keyframe manipulation
    curve6 = Curve()
    curve6[0] = 1
    assert curve6[0] == 1

    # setting custom interp method directly
    curve7 = Curve()
    curve7[0] = lambda x: x
    assert curve7[0] == 0
    
    # Test interpolation
    #curve8 = Curve(((0,0), (1,1)))
    #curve8 = Curve(((0,0, 'linear'), (1,1)))
    #curve8 = Curve((Keyframe(0,0, 'linear'), (1,1)))
    curve8 = Curve({0:Keyframe(0,0, 'linear'), 1:1})
    assert curve8[0.5] == 0.5
