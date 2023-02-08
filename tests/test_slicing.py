from keyframed import Curve, ParameterGroup, Composition
import pytest
from loguru import logger

EPS = 1e-9

def test_simple_slicing():
    c0=Curve()
    assert c0 == c0[:]

def test_interpolated_slicing_left():
    c0=Curve({10:10}, default_interpolation='linear')
    c1 = c0[:5]
    for i in range(6):
        #assert c0[i] == c1[i]
        assert abs(c0[i] - c1[i]) < EPS
    assert c1[6] == 5

def test_interpolated_slicing_right():
    c0=Curve({10:10}, default_interpolation='linear')
    k = 5
    c1 = c0[k:]
    print(c1._data)
    for i in range(10):
        j = i-k
        if j < 0:
            continue
        assert c0[i] == c1[j]

# pgroup slicing
def test_simple_pgroup_slicing():
    c0=Curve(label='foo')
    c1=Curve(label='bar')
    pg0 = ParameterGroup((c0,c1))
    pg1 = pg0[:]
    print(pg0.to_dict())
    print(pg1.to_dict())
    assert pg0 == pg1

def test_pgroup_interpolated_slicing_left():
    c0=Curve({10:10}, default_interpolation='linear', label='foo')
    c1=Curve(label='bar')
    pg0 = ParameterGroup((c0,c1))
    pg1 = pg0[:5]
    #print(pg0.to_dict())
    #print(pg1.to_dict())
    for i in range(6):
        for label in pg0.parameters:
            assert abs(pg0[i][label] - pg1[i][label]) < EPS
    assert pg0[10] == {'foo': 10, 'bar': 0}
    assert pg1[10] == {'foo': 5, 'bar': 0}

def test_pgroup_interpolated_slicing_right():
    c0=Curve({10:10}, default_interpolation='linear', label='foo')
    c1=Curve(label='bar')
    pg0 = ParameterGroup((c0,c1))
    k = 5
    pg1 = pg0[k:]
    for i in range(10):
        j = i-k
        if j < 0:
            continue
        for label in pg0.parameters:
            assert abs(pg0[i][label] - pg1[j][label])  < EPS

# comp slicing
def test_simple_comp_slicing():
    c0=Curve(1, label='foo')
    c1 = c0 + 1
    c2 = c1[:]
    assert c1 == c2

def test_comp_interpolated_slicing_left():
    c0=Curve({10:10}, default_interpolation='linear', label='foo')
    #c1 = c0 + 1
    c1 = c0 + Curve(1) # just to be sure
    k=5
    c2 = c1[:k]
    for i in range(k+1):
        assert abs(c2[i] - c1[i]) < EPS
    assert c2[k+1] == c1[k]

# compositional pgroup slicing

def test_comp_pgroup_interpolated_slicing_right():
    c0=Curve({10:10}, default_interpolation='linear', label='foo')
    c1=Curve(label='bar')
    pg0 = ParameterGroup((c0,c1)) 
    pg1 = pg0 + Curve(1)
    k = 5
    pg2 = pg1[k:]
    for i in range(10):
        j = i-k
        if j < 0:
            continue
        for label in pg0.parameters:
            assert abs(pg1[i][label] - pg2[j][label])  < EPS