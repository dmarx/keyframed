import pytest
from keyframed.curve import Curve, EasingFunction, EaseIn, EaseOut

EPS = 1e-9

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
    curve = Curve({1:1}, ease_in=lambda x:x)
    assert curve.ease_in.use_easing(0.5) == True
    assert curve.ease_in.use_easing(1.5) == False

def test_EaseOut_get_ease_start_t():
    curve = Curve({1:1,2:0})
    assert curve.ease_out.get_ease_start_t() == 1

def test_EaseOut_get_ease_end_t():
    curve = Curve({1:1,2:0})
    assert curve.ease_out.get_ease_end_t() == 2

def test_EaseOut_use_easing():
    curve = Curve({1:1,2:0}, ease_out=lambda x:x)
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


def test_actual_use_case1():
    import math
    def sin2(t):
        return math.sin(t * math.pi / 2) ** 2
    def cos2(t):
        return math.cos(t * math.pi / 2) ** 2
    curve = Curve({0:1, 30:0.5, 50:0}, default_interpolation='linear', ease_in=sin2, ease_out=cos2)
    #print(curve.ease_in.start_t, curve.ease_in.end_t)
    #print(curve.ease_out.start_t, curve.ease_out.end_t)
    #xs = list(range(50))
    #ys = [curve[x] for x in xs]
    #for x,y in zip(xs,ys):
    #    print(x,y)
    #assert False
    assert curve[3] == 0.95
    assert curve[15] == 0.75
    assert curve[40] == 0.25 # this would be true for lerp as well...
    assert abs(curve[34] -  0.4522542485937368) < EPS

def test_actual_use_case2():
    import math
    def sin2(t):
        return math.sin(t * math.pi / 2) ** 2
    def cos2(t):
        return math.cos(t * math.pi / 2) ** 2
    curve = Curve({20:0, 40:1, 70:0}, default_interpolation='linear', ease_in=sin2, ease_out=cos2)
    # print(curve.ease_in.start_t, curve.ease_in.end_t)
    # print(curve.ease_out.start_t, curve.ease_out.end_t)
    # xs = list(range(70))
    # ys = [curve[x] for x in xs]
    # for x,y in zip(xs,ys):
    #     print(x,y)
    # assert False
    assert curve[19] == 0
    assert curve[20] == 0
    assert abs(curve[28] - 0.3454915028125264) < EPS
    assert abs(curve[30] - 0.5) < EPS
    assert curve[40] == 1
    assert abs(curve[48] - 0.834565303179429) < EPS
    assert abs(curve[50] -  0.75) < EPS
    assert abs(curve[55] -  0.5) < EPS
    assert curve[70] == 0
    # yeah I def need to do something about this.
    assert curve[80] == 0 # throws an index error. probably not great.