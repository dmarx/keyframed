from keyframed import Curve, ParameterGroup


def test_parameter_group_init():
    pgroup = ParameterGroup({'p1': 1, 'p2': 2})
    #assert pgroup.weight[0].value == 1
    assert pgroup.weight[0] == 1
    assert pgroup[0] == {'p1': 1, 'p2': 2}
    assert pgroup[10] == {'p1': 1, 'p2': 2}

    pgroup = ParameterGroup((Curve(1,label='foo'), Curve(2, label='bar')))
    assert pgroup.weight[0] == 1
    assert pgroup[0] == {'foo': 1, 'bar': 2}
    assert pgroup[10] == {'foo': 1, 'bar': 2}


def test_parameter_group_getitem():
    pgroup = ParameterGroup({'p1': 1, 'p2': 2}, weight=2)
    assert pgroup[0] == {'p1': 2, 'p2': 4}


def test_pgroup_nontrivial():
    pgroup = ParameterGroup({'p1': 1, 'p2': 2}, weight=2)
    assert pgroup.weight[0] == 2
    assert pgroup.weight[1] == 2
    assert pgroup[0] == {'p1': 2, 'p2': 4}
    assert pgroup[1] == {'p1': 2, 'p2': 4}

def test_pgroup_of_loops():
    curve = Curve([(0,0),(2,2)], loop=True, default_interpolation='linear')
    pgroup = ParameterGroup({'p1': curve})
    for i in range(10):
        assert pgroup[i]['p1'] == curve[i]

def test_pgroup_loop():
    curve = Curve([(0,0),(2,2)], default_interpolation='linear')
    curve_loop = curve.copy()
    curve_loop.loop = True
    pgroup = ParameterGroup({'p1': curve}, loop=True)
    for i in range(10):
        assert pgroup[i]['p1'] == curve_loop[i]

def test_pgroup_bounce():
    curve = Curve([(0,0),(2,2)], default_interpolation='linear')
    curve_loop = curve.copy()
    curve_loop.bounce = True
    pgroup = ParameterGroup({'p1': curve}, bounce=True)
    for i in range(10):
        assert pgroup[i]['p1'] == curve_loop[i]

def test_pgroup_of_bounces():
    curve = Curve([(0,0),(2,2)], bounce=True, default_interpolation='linear')
    pgroup = ParameterGroup({'p1': curve})
    for i in range(10):
        assert pgroup[i]['p1'] == curve[i]