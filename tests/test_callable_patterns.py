"""
Testing recipes for fancy applications of callable getters
"""

from keyframed import Keyframed

TEST_EPS = 1e-8

# implement fibonnaci
def test_fib():
    fib_seq = Keyframed({0:1,1:1})
    def fib_get(k, K):
        return K[k-1]+K[k-2]
    fib_seq[2] = fib_get
    assert fib_seq[0] == 1
    assert fib_seq[1] == 1
    assert fib_seq[2] == 2
    assert fib_seq[3] == 3
    assert fib_seq[4] == 5
    assert fib_seq[8] == 34

def test_fib_jump():
    fib_seq = Keyframed({0:1,1:1})
    def fib_get(k, K):
        return K[k-1]+K[k-2]
    fib_seq[2] = fib_get
    assert fib_seq[8] == 34



# polynomial interpolation
# https://docs.scipy.org/doc/scipy/tutorial/interpolate.html
from scipy.interpolate import interp1d

def test_quad():
    #seq={0:1,1:2, 3:8, 4:16} # this is exponential growth, not quadratic
    seq={0:0,1:1,3:9,4:16}
    K = Keyframed(seq)
    #xs = list(K.keyframes)
    #ys = [K[i] for i in xs]
    def quad_interp(k, K, xs, ys):
        print(xs)
        print(ys)
        f = interp1d(xs, ys, kind='quadratic')
        return f(k).item()
    K[2]=quad_interp
    #assert abs(K[2] - 4) < TEST_EPS
    assert 4-TEST_EPS <= K[2] <= 4+TEST_EPS

# windowed average


# EMA


# exponential interpolation
