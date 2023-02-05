from keyframed import Curve, Keyframe
from keyframed.curve import ensure_sorteddict_of_keyframes


import pytest
from sortedcontainers import SortedDict


TEST_EPS = 1e-8


def test_curve():
    c = Curve()

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


# lazy chatgpt tests


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
    
    # Test improperly formed list input
    curve = [0,1]
    #with pytest.raises(NotImplementedError):
    with pytest.raises(TypeError):
        ensure_sorteddict_of_keyframes(curve)

# def test_Keyframe():
#     # Test addition
#     kf1 = Keyframe(t=0, value=0)
#     kf2 = Keyframe(t=0, value=1)
#     assert (kf1 + kf2) == 1
#     assert (kf1 + 1) == 1
#     assert (1 + kf1) == 1
    
#     # Test comparison
#     kf1 = Keyframe(t=0, value=0)
#     kf2 = Keyframe(t=0, value=1)
#     assert kf1 <= kf2
#     assert kf1 < kf2
#     assert kf2 >= kf1

#     # Test arithmetic operations
#     kf1 = Keyframe(t=0, value=0)
#     kf2 = Keyframe(t=1, value=1)
#     assert (kf1 + kf2) == 1
#     assert (kf1 + 1) == 1
#     assert (1 + kf1) == 1
#     assert (kf1 * kf2) == 0
#     assert (kf1 * 2) == 0
#     assert (2 * kf1) == 0
#     assert (kf1 <= kf2) == True
#     assert (kf1 <= 1) == True
#     assert (1 <= kf1) == False
#     assert (kf1 >= kf2) == False
#     assert (kf1 >= 1) == False
#     assert (1 >= kf1) == True
#     assert (kf1 < kf2) == True
#     assert (kf1 < 1) == True
#     assert (1 < kf1) == False
#     assert (kf1 > kf2) == False
#     assert (kf1 > 1) == False
#     assert (1 > kf1) == True
#     assert (kf1 == kf2) == False
#     assert (kf1 == 1) == False
#     assert (1 == kf1) == False
    
#     # Test equality and string representation
#     kf1 = Keyframe(t=0, value=0, interpolation_method='previous')
#     kf2 = Keyframe(t=0, value=0, interpolation_method='previous')
#     kf3 = Keyframe(t=1, value=0, interpolation_method='previous')
#     assert kf1 == kf2
#     assert kf1 == kf3 # whether or not this SHOULD evaluate to true is a different question. ChatGPT disagress with me.
#     assert str(kf1) == "Keyframe(t=0, value=0, interpolation_method='previous')"

def test_curve():
    # Test basic curve construction
    curve1 = Curve()
    assert curve1.duration == 0
    assert list(curve1.keyframes) == [0]
    assert list(curve1.values) == [0]
    
    curve2 = Curve(duration=5)
    assert curve2.duration == 5
    assert list(curve2.keyframes) == [0]
    assert list(curve2.values) == [0]
    
    curve3 = Curve(((0,0), (2,2)))
    assert curve3.duration == 2
    assert list(curve3.keyframes) == [0, 2]
    assert list(curve3.values) == [0, 2]
    
    curve4 = Curve({0:0, 2:2})
    assert curve4.duration == 2
    assert list(curve4.keyframes) == [0, 2]
    assert list(curve4.values) == [0, 2]
    
def test_curve_loop():
    # Test looping behavior
    curve5 = Curve(duration=5, loop=True)
    assert curve5[5] == curve5[0]
    
def test_curves_setitem():
    # Test keyframe manipulation
    curve6 = Curve()
    curve6[0] = 1
    assert curve6[0] == 1

def test_curve_set_interp_callable():
    # setting custom interp method directly
    curve7 = Curve()
    curve7[0] = lambda x: x
    assert curve7[0] == 0
    
def test_curve_interpolation():
    # Test interpolation
    #curve8 = Curve(((0,0), (1,1)))
    #curve8 = Curve(((0,0, 'linear'), (1,1))) # this one still not a thing
    #assert curve8[0.5] == 0.5
    curve8 = Curve((Keyframe(0,0, 'linear'), (1,1)))
    assert curve8[0.5] == 0.5
    curve8 = Curve({0:Keyframe(0,0, 'linear'), 1:1})
    assert curve8[0.5] == 0.5


###############################


