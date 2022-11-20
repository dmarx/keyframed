import pytest

from keyframed import Keyframed

def test_knn():
    K = Keyframed({k:1 for k in [0,1,2,3,7,8,9]})
    assert not K.is_bounded
    assert K.keyframes.__len__() == 7
    assert not hasattr(K, '_tree')
    neighbors = K.keyframes_neighborhood(4, order=2)
    assert neighbors == [2,3]
    assert hasattr(K, '_tree')
    neighbors = K.keyframes_neighborhood(3.9, order=3)
    assert neighbors == [1,2,3]
    neighbors = K.keyframes_neighborhood(4.1, order=3)
    assert neighbors == [2,3,7]

def test_knn_balanced():
    K = Keyframed({k:1 for k in [0,1,2,3,7,8,9]})
    assert not K.is_bounded
    assert K.keyframes.__len__() == 7
    assert not hasattr(K, '_tree')
    neighbors = K.keyframes_neighborhood_balanced(4, order=2)
    assert neighbors == [3,7]
    assert not hasattr(K, '_tree')
    neighbors = K.keyframes_neighborhood_balanced(3.9, order=3)
    assert neighbors == [2,3,7]
    neighbors = K.keyframes_neighborhood_balanced(4.1, order=3)
    assert neighbors == [2,3,7]
    neighbors = K.keyframes_neighborhood_balanced(4, order=4)
    assert neighbors == [2,3,7,8]
