"""
Testing recipes for fancy applications of callable getters
"""

from keyframed import Keyframed

# implement fibonnaci
def test_fib():
    fib_seq = Keyframed({0:1,1:1})
    def fib_get(k, K=fib_seq):
        return K[k-1]+K[k-2]
    fib_seq[2] = fib_get
    assert fib_seq[0] == 1
    assert fib_seq[1] == 1
    assert fib_seq[2] == 2
    assert fib_seq[3] == 3
    assert fib_seq[4] == 5
    #assert fib_seq[5] == 8
    #assert fib_seq[6] == 13
    #assert fib_seq[7] == 21
    assert fib_seq[8] == 34
    # holy shit, it works. how do I add memoization?

def test_fib_jump():
    fib_seq = Keyframed({0:1,1:1})
    def fib_get(k, K=fib_seq):
        return K[k-1]+K[k-2]
    fib_seq[2] = fib_get
    assert fib_seq[8] == 34


# windowed average


# EMA


# exponential interpolation
