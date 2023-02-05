from keyframed import Curve


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


# __sub__

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