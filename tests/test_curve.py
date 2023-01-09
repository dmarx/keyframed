from keyframed import Curve, Prompt, ParameterGroup

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

