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

def test_parameter_group_arithmetic_operations1():
    pgroup = ParameterGroup({'p1': 1, 'p2': 2}, weight=2)
    pgroup_copy = pgroup + 1
    assert pgroup_copy[0]['p1'] == 4

    pgroup = ParameterGroup({'p1': Curve(1), 'p2': Curve(2)}, weight=2)
    pgroup_copy = pgroup + 1
    assert pgroup_copy[0]['p1'] == 4


def test_parameter_group_getitem():
    pgroup = ParameterGroup({'p1': 1, 'p2': 2}, weight=2)
    assert pgroup[0] == {'p1': 2, 'p2': 4}



def test_parameter_group_arithmetic_operations():
    # I think this test is a duplicate of test_parameter_group_arithmetic_operations1
    #pgroup = ParameterGroup({'p1': 1, 'p2': 2}, weight=2)
    pgroup = ParameterGroup({'p1': Curve(1), 'p2': Curve(2)}, weight=2) # not the issue
    pgroup_copy = pgroup + 1
    print(pgroup_copy.label)
    assert pgroup.weight[0] == 2
    assert pgroup_copy[0]['p1'] == 4
    assert pgroup_copy[0]['p2'] == 6

    assert pgroup.weight[0] == 2
    pgroup_copy2 = pgroup * 3
    #assert pgroup_copy2.weight[0] == 6 # naw fuck this. need the behavior to be consistent with addition.
    assert pgroup_copy2.weight[0] == 2

    pgroup_copy = 3 + pgroup
    assert pgroup_copy.weight[0] == 2
    assert pgroup_copy[0]['p1'] == 8
    assert pgroup_copy[0]['p2'] == 10

    pgroup_copy = 3 * pgroup
    assert pgroup_copy.weight[0] == 2
    assert pgroup_copy[0]['p1'] == 6
    assert pgroup_copy[0]['p2'] == 12

def test_pgroup_nontrivial():
    pgroup = ParameterGroup({'p1': 1, 'p2': 2}, weight=2)
    assert pgroup.weight[0] == 2
    assert pgroup.weight[1] == 2
    assert pgroup[0] == {'p1': 2, 'p2': 4}
    assert pgroup[1] == {'p1': 2, 'p2': 4}

###############################################
