from keyframed.serialization import from_dict, to_yaml, from_yaml
from keyframed import Keyframe, Curve, ParameterGroup, Composition


def test_kf_from_dict():
    kf = Keyframe(t=0, value=1, interpolation_method='foobar')
    d = kf.to_dict()
    kf2 = from_dict(d)
    assert kf2.t == kf.t
    assert kf2.value == kf.value
    assert kf2.interpolation_method == kf.interpolation_method

def test_curve_from_dict():
    c = Curve(1, label='foo')
    d = c.to_dict()
    c2 = from_dict(d)
    assert c.label == c2.label
    assert c.loop == c2.loop
    assert c.duration == c2.duration
    assert c._data == c2._data # NB: __eq__ ignores interpolation methods I think
    assert c == c2

def test_pgroup_curves_from_dict():
    c1 = Curve(label='foo')
    c2 = Curve(label='bar')
    c3 = ParameterGroup((c1, c2))
    d = c3.to_dict()
    print(d)
    print(d.keys())
    c4 = from_dict(d)
    print(c4)
    #raise
    # to do: add equality methods to the classes
    assert c3 == c4
    # this really deserves its own separate test (for __eq__)
    c3.label = 'baz'
    assert c1 != c4

############################################


def test_pgroup_from_yamldict():
    c1 = Curve(label='foo')
    c2 = Curve(label='bar')
    c3 = ParameterGroup((c1, c2))
    d = c3.to_dict(simplify=False, for_yaml=True)
    print(d)
    assert d == {'parameters': {'foo': {'curve': ((0, 0, 'previous'),), 'loop': False, 'duration': 0, 'label': 'foo'}, 'bar': {'curve': ((0, 0, 'previous'),), 'loop': False, 'duration': 0, 'label': 'bar'}}, 'weight': {'curve': ((0, 1, 'previous'),), 'loop': False, 'duration': 0, 'label': 'pgroup(foo,bar)_WEIGHT'}, 'label': 'pgroup(foo,bar)'}
    c4 = from_dict(d)
    assert c3 == c4

from keyframed import SmoothCurve

def test_compositional_pgroup_from_yamldict():
    low, high = 0.0001, 0.3
    step1 = 50
    step2 = 2 * step1
    curves = ParameterGroup((
        SmoothCurve({0:low, (step1-1):high, (2*step1-1):low}, loop=True),
        SmoothCurve({0:high, (step1-1):low, (2*step1-1):high}, loop=True),

        SmoothCurve({0:low, (step2-1):high, (2*step2-1):low}, loop=True),
        SmoothCurve({0:high, (step2-1):low, (2*step2-1):high}, loop=True),
    ))
    curves2 = curves + 1
    d = curves2.to_dict(simplify=False, for_yaml=True)
    curves3 = from_dict(d)
    assert curves2 == curves3


##############################################################################


def test_curve_to_yaml():
    c1 = Curve({1:1}, label='foo', default_interpolation='linear')
    txt = to_yaml(c1, simplify=False)
    print(txt)
    assert txt.strip() == """curve:
- - 0
  - 0
  - linear
- - 1
  - 1
  - linear
loop: false
duration: 1
label: foo"""

def test_curve_sum_to_yaml():
    c0 = Curve({1:1}, label='foo', default_interpolation='linear')
    c1 = c0 + 1
    c2 = 1 + c0
    txt1 = to_yaml(c1, simplify=False)
    txt2 = to_yaml(c2, simplify=False)
    assert txt1 == txt2
    assert txt1.strip() == """curve:
- - 0
  - 1
  - linear
- - 1
  - 2
  - linear
loop: false
duration: 1
label: foo"""

def test_curve_prod_to_yaml():
    c0 = Curve({1:1}, label='foo', default_interpolation='linear')
    c1 = c0 * 1
    c2 = 1 * c0

    for c in (c1, c2):
        for curvename in list(c.parameters.keys()):
            if curvename != 'foo':
                print(curvename)
                assert curvename.startswith('curve_')
                thiscurve = c.parameters.pop(curvename)
                thiscurve.label = 'bar'
                c.parameters[thiscurve.label] = thiscurve
        
    txt1 = to_yaml(c1, simplify=False)
    txt2 = to_yaml(c2, simplify=False)
    print(txt1)
    print(txt2)
    
    assert txt1 == txt2
    assert txt1.strip() == """parameters:
  foo:
    curve:
    - - 0
      - 0
      - linear
    - - 1
      - 1
      - linear
    loop: false
    duration: 1
    label: foo
  bar:
    curve:
    - - 0
      - 1
      - previous
    loop: false
    duration: 0
    label: bar
weight:
  curve:
  - - 0
    - 1
    - previous
  loop: false
  duration: 0
  label: ( 1 * foo )_WEIGHT
label: ( 1 * foo )
reduction: multiply"""

def test_pgroup_to_yaml():
    low, high = 0.0001, 0.3
    step1 = 50
    curves = ParameterGroup({
        'foo':SmoothCurve({0:low, (step1-1):high, (2*step1-1):low}, loop=True),
        'bar':SmoothCurve({0:high, (step1-1):low, (2*step1-1):high}, loop=True)
    })
    txt = to_yaml(curves, simplify=False)
    print(txt)
    assert txt.strip() == """parameters:
  foo:
    curve:
    - - 0
      - 0.0001
      - eased_lerp
    - - 49
      - 0.3
      - eased_lerp
    - - 99
      - 0.0001
      - eased_lerp
    loop: true
    duration: 99
    label: foo
  bar:
    curve:
    - - 0
      - 0.3
      - eased_lerp
    - - 49
      - 0.0001
      - eased_lerp
    - - 99
      - 0.3
      - eased_lerp
    loop: true
    duration: 99
    label: bar
weight:
  curve:
  - - 0
    - 1
    - previous
  loop: false
  duration: 0
  label: pgroup(foo,bar)_WEIGHT
label: pgroup(foo,bar)"""


#############################################

def test_curve_to_yaml_simplified():
    c0 = Curve()
    txt = to_yaml(c0, simplify=True)
    assert txt.strip() == "curve: []"

    c1 = Curve({1:1}, label='foo', default_interpolation='linear')
    txt = to_yaml(c1, simplify=True)
    assert txt.strip() == """curve:
- - 0
  - 0
  - linear
- - 1
  - 1
label: foo"""

    c2 = Curve({1:1})
    txt = to_yaml(c2, simplify=True)
    assert txt.strip() == """curve:
- - 1
  - 1"""

    c3 = Curve(((1,1,'linear'),(2,2)))
    txt = to_yaml(c3, simplify=True)
    print(txt)
    assert txt.strip() == """curve:
- - 1
  - 1
  - linear
- - 2
  - 2"""

def test_curve_from_yaml():
    c0 = Curve()
    c1 = from_yaml(to_yaml(c0, simplify=False))
    assert c0 == c1

def test_curve_from_yaml_simplified():
    c0 = Curve()
    c1 = from_yaml(to_yaml(c0, simplify=True))
    assert c0.to_dict(simplify=True) == c1.to_dict(simplify=True)
    c1.label = c0.label
    assert c0 == c1

def test_curve_from_yaml_simplified2():
    c0 = Curve({1:1})
    c1 = from_yaml(to_yaml(c0, simplify=True))
    assert c0.to_dict(simplify=True) == c1.to_dict(simplify=True)
    c1.label = c0.label
    assert c0 == c1

def test_curve_from_yaml_simplified3():
    c0 = Curve({1:1}, default_interpolation='linear')
    c1 = from_yaml(to_yaml(c0, simplify=True))
    assert c0.to_dict(simplify=True) == c1.to_dict(simplify=True)
    c1.label = c0.label
    assert c0 == c1

def test_pgroup_to_yaml_simplified():
    low, high = 0.0001, 0.3
    step1 = 50
    curves = ParameterGroup({
        'foo':SmoothCurve({0:low, (step1-1):high, (2*step1-1):low}, loop=True),
        'bar':SmoothCurve({0:high, (step1-1):low, (2*step1-1):high}, loop=True)
    })
    txt = to_yaml(curves, simplify=True)
    print(txt)
    assert txt.strip() == """parameters:
  foo:
    curve:
    - - 0
      - 0.0001
      - eased_lerp
    - - 49
      - 0.3
    - - 99
      - 0.0001
    loop: true
  bar:
    curve:
    - - 0
      - 0.3
      - eased_lerp
    - - 49
      - 0.0001
    - - 99
      - 0.3
    loop: true"""
    # to do: 
    # - curve.label is redundant in parameter groups
    # - parameter groups need a `_using_default_label` flag like with curve
    # - `pgroup.weight == Curve(1)`` is redundant

def test_comp_pgroup_to_yaml_simplified():
    low, high = 0.0001, 0.3
    step1 = 50
    curves = ParameterGroup({
        'foo':SmoothCurve({0:low, (step1-1):high, (2*step1-1):low}, loop=True),
        'bar':SmoothCurve({0:high, (step1-1):low, (2*step1-1):high}, loop=True)
    })
    #curves2 = curves*1
    c_ = Curve(2, label="dummy")
    c1 = curves*c_
    c2 = c_*curves

    txt1 = to_yaml(c1, simplify=True)
    txt2 = to_yaml(c2, simplify=True)
    print(txt1)
    assert txt1 == txt2
    assert txt1.strip() == """parameters:
  foo:
    parameters:
      foo:
        curve:
        - - 0
          - 0.0001
          - eased_lerp
        - - 49
          - 0.3
        - - 99
          - 0.0001
        loop: true
      dummy:
        curve:
        - - 0
          - 2
    reduction: multiply
  bar:
    parameters:
      bar:
        curve:
        - - 0
          - 0.3
          - eased_lerp
        - - 49
          - 0.0001
        - - 99
          - 0.3
        loop: true
      dummy:
        curve:
        - - 0
          - 2
    reduction: multiply"""

def test_comp_pgroup_from_yaml_simplified():
    low, high = 0.0001, 0.3
    step1 = 50
    curves = ParameterGroup({
        'foo':SmoothCurve({0:low, (step1-1):high, (2*step1-1):low}, loop=True),
        'bar':SmoothCurve({0:high, (step1-1):low, (2*step1-1):high}, loop=True)
    })
    #curves2 = curves*1
    c_ = Curve(2, label="dummy")
    c1 = curves*c_
    txt1 = to_yaml(c1, simplify=True)
    print(txt1)
    ### everything above this copied from test_comp_pgroup_to_yaml_simplified
    c2 = from_yaml(txt1)
    #assert c1 == c2
    #assert c1.to_dict(simplify=True) == c2._to_dict(simplify=True) # to do: fix this
    txt2 = to_yaml(c2, simplify=True)
    assert txt1 == txt2