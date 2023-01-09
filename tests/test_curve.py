from keyframed import Curve, Prompt, ParameterGroup, get_register_interpolation_method, Keyframe

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
    #fib_seq = Keyframed({0:1,1:1})
    def fib_get(k, K):
        return K[k-1]+K[k-2]
    #fib_seq[2] = fib_get
    get_register_interpolation_method('fib_get', fib_get)
    #fib_seq = Keyframed({0:1,1:Keyframe(t=1, value=1, interpolation_method='fib_get')})
    fib_seq = Keyframed({0:Keyframe(t=0, value=1, interpolation_method='fib_get')})
    fib_seq[1]=1
    #fib_seq = Keyframed({0:1,1:Keyframe(t=1, value=1, interpolation_method=fib_get)})
    assert fib_seq[0] == 1
    assert fib_seq[1] == 1
    assert fib_seq[2] == 2
    assert fib_seq[3] == 3
    assert fib_seq[4] == 5
    assert fib_seq[8] == 34

# def test_fib_jump():
#     fib_seq = Keyframed({0:1,1:1})
#     def fib_get(k, K):
#         return K[k-1]+K[k-2]
#     fib_seq[2] = fib_get
#     assert fib_seq[8] == 34

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
    get_register_interpolation_method('quad_interp', quad_interp)
    K[1] = Keyframe(t=1, value=1, interpolation_method='quad_interp')
    print(K[2])
    assert 4-TEST_EPS <= K[2] <= 4+TEST_EPS
