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

def test_quad_explicit():
    seq={0:0,1:1,3:9,4:16}
    K = Keyframed(seq)
    def quad_interp(k, K, xs, ys):
        f = interp1d(xs, ys, kind='quadratic')
        return f(k).item()
    K[2]=quad_interp
    assert 4-TEST_EPS <= K[2] <= 4+TEST_EPS

def test_quad_implicit():
    seq={0:0,1:1,3:9,4:16}
    K = Keyframed(seq)
    K[2] = None,'quadratic'
    print(K[2])
    assert 4-TEST_EPS <= K[2] <= 4+TEST_EPS

from loguru import logger

# windowed average
def test_windowed_avg_centered():
    windowlen=3
    def windowed_avg(k,K:Keyframed,xs,ys):
        context = K.keyframes_neighborhood_balanced(k, order=windowlen-1)
        logger.debug(context)
        return sum([K[i] for i in context])/len(context)
    seq={0:0,1:1,3:2,5:2,6:2,8:1}
    K=Keyframed(data=seq)
    for k,v in seq.items():
        assert K[k] == v
    # default interp is previous
    assert K[2] == 1
    assert K[4] == 2
    assert K[7] == 2
    ###################
    K[2] = K[4] = K[7] = windowed_avg
    assert K[2] == 1.5
    assert K[4] == 2
    assert K[7] == 1.5




def test_windowed_avg_trailing():
    pass

def test_windowed_avg_leading():
    pass

# EMA


# exponential interpolation
