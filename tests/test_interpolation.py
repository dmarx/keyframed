import pytest

from keyframed import Curve, Keyframe

from keyframed.interpolation import (
    register_interpolation_method, 
    bisect_left_value, 
    INTERPOLATORS
)


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


# implement fibonnaci
def test_fib():
    def fib_get(k, K):
        return K[k-1]+K[k-2]

    #fib_seq[2] = fib_get
    register_interpolation_method('fib_get', fib_get)
    fib_seq = Curve({0:Keyframe(t=0, value=1, interpolation_method='fib_get')})
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
    fib_seq = Curve({0:Keyframe(t=0, value=1, interpolation_method='fib_get')})
    fib_seq[1]=1
    assert fib_seq[8] == 34

# from scipy.interpolate import interp1d

# def test_quad_explicit():
#     seq={0:0,1:1,3:9,4:16}
#     K = Keyframed(seq)
#     def quad_interp(k, K):
#         xs = list(K.keyframes)
#         ys = list(K.values)
#         f = interp1d(xs, ys, kind='quadratic')
#         return f(k).item()
#     #K[2]=quad_interp
#     register_interpolation_method('quad_interp', quad_interp)
#     K[1] = Keyframe(t=1, value=1, interpolation_method='quad_interp')
#     print(K[2])
#     assert 4-TEST_EPS <= K[2] <= 4+TEST_EPS

###############################


def test_Curve_default_interpolation():
    curve = Curve(default_interpolation='previous')
    assert curve.default_interpolation == 'previous'
    curve = Curve(default_interpolation='linear')
    assert curve.default_interpolation == 'linear'
    curve = Curve(default_interpolation='next')
    assert curve.default_interpolation == 'next'
    # with pytest.raises(ValueError) as e:
    #     curve = Curve(default_interpolation='invalid')
    # assert str(e.value) == "default_interpolation must be one of 'previous', 'linear', 'next'"
    curve = Curve()
    assert curve.default_interpolation == 'previous'
    
def test_Curve_default_interpolation_with_values():
    curve = Curve(((0,0), (1,1)), default_interpolation='previous')
    assert curve[0.5] == 0
    curve = Curve(((0,0), (1,1)), default_interpolation='linear')
    assert curve[0.5] == 0.5
    curve = Curve(((0,0), (1,1)), default_interpolation='next')
    assert curve[0.5] == 1
    
def test_curve_default_interpolation_longer():
    curve = Curve({0:1, 30:0.5, 50:0}, default_interpolation='linear')
    assert curve[0] == 1
    assert curve[30] == 0.5
    assert curve[50] == 0
    assert curve._data[0].interpolation_method == 'linear'
    assert curve._data[30].interpolation_method == 'linear'
    assert curve._data[50].interpolation_method == 'linear'
    for x in range(31):
        print(f"{x}:{curve[x]}")
    assert curve[15] == 0.75
    assert curve[40] == 0.25


def test_curve_w_kf_specified_interpolator():
    c1 = Curve({0:1, 5:Keyframe(t=5,value=1,interpolation_method='linear'), 9:5})
    assert c1[7] == 3

###############