from keyframed import Curve, ParameterGroup


def test_curve_to_curve_add():
    curve0 = Curve({0:0, 2:2})
    assert curve0[0] == 0
    assert curve0[1] == 0
    assert curve0[2] == 2

    curve1 = Curve({1:1})
    assert curve1[0] == 0
    assert curve1[1] == 1
    assert curve1[2] == 1

    curve2 = curve0 + curve1
    assert curve2[0] == 0
    assert curve2[1] == 1
    assert curve2[2] == 3


def test_sub_curve():
    c1 = Curve({0:1})
    c2 = Curve({0:2})
    assert (c2 - c1)[0] == 1
    assert (c1 - c2)[0] == -1

    assert (c2 - 1)[0] == 1
    assert (1 - c2)[0] == -1

def test_sub_pgroup():
    pass

def test_sub_composition():
    pass


def test_parameter_group_arithmetic_operations1():
    pgroup = ParameterGroup({'p1': 1, 'p2': 2}, weight=2)
    pgroup_copy = pgroup + 1
    assert pgroup.weight[0] == 2
    assert pgroup_copy[0]['p1'] == 4
    assert pgroup_copy[0]['p2'] == 6

    pgroup = ParameterGroup({'p1': Curve(1), 'p2': Curve(2)}, weight=2)
    pgroup_copy = pgroup + 1
    assert pgroup.weight[0] == 2
    assert pgroup_copy[0]['p1'] == 4
    assert pgroup_copy[0]['p2'] == 6



def test_parameter_group_arithmetic_operations():
    # I think this test is a duplicate of test_parameter_group_arithmetic_operations1
    #pgroup = ParameterGroup({'p1': 1, 'p2': 2}, weight=2)
    pgroup = ParameterGroup({'p1': Curve(1), 'p2': Curve(2)}, weight=2) # not the issue
    pgroup_copy = pgroup + 1

    pgroup_copy2 = pgroup * 3
    assert pgroup_copy2.weight[0] == 2

    pgroup_copy = 3 + pgroup
    assert pgroup_copy.weight[0] == 2
    assert pgroup_copy[0]['p1'] == 8
    assert pgroup_copy[0]['p2'] == 10

    pgroup_copy = 3 * pgroup
    assert pgroup_copy.weight[0] == 2
    assert pgroup_copy[0]['p1'] == 6
    assert pgroup_copy[0]['p2'] == 12