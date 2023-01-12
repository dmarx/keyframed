import pytest
from keyframed.curve import Curve, EasingFunction, EaseIn, EaseOut

def test_EasingFunction_init():
    f = lambda x: x
    curve = Curve()
    start_t = 0
    end_t = 1
    easing_function = EasingFunction(f, curve, start_t, end_t)
    assert easing_function.f == f
    assert easing_function.curve == curve
    assert easing_function._start_t == start_t
    assert easing_function._end_t == end_t

def test_EasingFunction_start_t():
    f = lambda x: x
    curve = Curve()
    start_t = 0
    end_t = 1
    easing_function = EasingFunction(f, curve, start_t, end_t)
    assert easing_function.start_t == start_t
    easing_function = EasingFunction(f, curve)
    assert easing_function.start_t == 0

def test_EasingFunction_end_t():
    f = lambda x: x
    curve = Curve()
    start_t = 0
    end_t = 1
    easing_function = EasingFunction(f, curve, start_t, end_t)
    assert easing_function.end_t == end_t
    easing_function = EasingFunction(f, curve)
    assert easing_function.end_t == 0

def test_EaseIn_get_ease_start_t():
    curve = Curve()
    ease_in = EaseIn(curve)
    assert ease_in.get_ease_start_t() == 0

def test_EaseIn_get_ease_end_t():
    curve = Curve({1:1})
    assert curve.ease_in.get_ease_end_t() == 1

def test_EaseIn_use_easing():
    curve = Curve({1:1})
    assert curve.ease_in.use_easing(0.5) == True
    assert curve.ease_in.use_easing(1.5) == False

def test_EaseOut_get_ease_start_t():
    curve = Curve({1:1,2:0})
    assert curve.ease_out.get_ease_start_t() == 1

def test_EaseOut_get_ease_end_t():
    curve = Curve({1:1,2:0})
    assert curve.ease_out.get_ease_end_t() == 2

def test_EaseOut_use_easing():
    curve = Curve({1:1,2:0})
    assert curve.ease_out.use_easing(1.5) == True
    assert curve.ease_out.use_easing(2.5) == False

# def test_EasingFunction_call():
#     f = lambda x: x**2
#     curve = Curve()
#     start_t = 0
#     end_t = 1
#     easing_function = EasingFunction(f, curve, start_t, end_t)
#     assert easing_function(0.5) == 0.25
#     assert easing_function(1) == 1
#     assert easing_function(0) == 0

# def test_EasingFunction_none_start_end_t():
#     f = lambda x: x**2
#     curve = Curve()
#     easing_function = EasingFunction(f, curve)
#     assert easing_function.start_t == None
#     assert easing_function.end_t == None
#     assert easing_function.get_ease_start_t() == None
#     assert easing_function.get_ease_end_t() == None

# def test_EasingFunction_none_curve():
#     f = lambda x: x**2
#     start_t = 0
#     end_t = 1
#     easing_function = EasingFunction(f, None, start_t, end_t)
#     assert easing_function.start_t == start_t
#     assert easing_function.end_t == end_t
#     assert easing_function.curve == None
#     assert easing_function.get_ease_start_t() == None
#     assert easing_function.get_ease_end_t() == None

# def test_EasingFunction_none_f():
#     curve = Curve()
#     start_t = 0
#     end_t = 1
#     with pytest.raises(TypeError) as e:
#         easing_function = EasingFunction(None, curve, start_t, end_t)
#     assert str(e.value) == "f must be callable"
#     with pytest.raises(TypeError) as e:
#         easing_function = EasingFunction("not callable", curve, start_t, end_t)
#     assert str(e.value) == "f must be callable"
    
# def test_EaseIn_none_curve():
#     curve = None
#     with pytest.raises(TypeError) as e:
#         ease_in = EaseIn(curve)
#     assert str(e.value) == "curve must be a valid object"
#     curve = Curve()
#     curve.keyframes = []
#     with pytest.raises(TypeError) as e:
#         ease_in = EaseIn(curve)
#     assert str(e.value) == "curve must be a valid object"

# def test_EaseOut_none_curve():
#     curve = None
#     with pytest.raises(TypeError) as e:
#         ease_out = EaseOut(curve)
#     assert str(e.value) == "curve must be a valid object"
#     curve = Curve()
#     curve.keyframes = []
#     with pytest.raises(TypeError) as e:
#         ease_out = EaseOut(curve)
#     assert str(e.value) == "curve must be a valid object"
    
def test_EaseIn_use_easing_out_of_range():
    curve = Curve({1:1})
    #assert curve.ease_in.use_easing(-1) == False
    assert curve.ease_in.use_easing(2) == False

def test_EaseOut_use_easing_out_of_range():
    curve = Curve({1:1, 2:0})
    #assert curve.ease_out.use_easing(-1) == False
    assert curve.ease_out.use_easing(3) == False

# def test_Curve_none_curve():
#     with pytest.raises(TypeError) as e:
#         curve = Curve(None)
#     assert str(e.value) == "curve must be a valid object"


