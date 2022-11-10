import pytest

from keyframed import Keyframed

def test_import():
    from keyframed import Keyframed

def test_init():
    k = Keyframed()
    assert not k.is_bounded
    assert k.__len__() is None
    assert list(k.keyframes) == [0]


def test_bounded():
    n=10
    k = Keyframed(n=n)
    assert len(k) == n

def test_set_unbounded():
      n=10
      k = Keyframed(n=n)
      assert len(k) == n
      k.set_unbounded()
      assert k.__len__() is None

#################

def test_data_unbounded():
    k = Keyframed(
        data={0:1, 15:2},
        #interp={5:'linear', 10:'previous'},
    )
    assert not k.is_bounded
    assert k.__len__() is None
    assert list(k.keyframes) == [0,15]
    assert k[0] == k[10] == 1
    assert k[15] == k[20] == 2

def test_data_interp_unbounded():
    k = Keyframed(
        data={0:1, 15:2},
        interp={5:'linear', 15:'previous'},
    )
    assert not k.is_bounded
    assert k.__len__() is None
    assert list(k.keyframes) == [0,5,15]
    assert k[0] == k[2] == k[4] == 1
    assert 1 < k[5] < k[10] < k[15]
    assert k[15] == k[20] == 2

###########################################

def test_data_bounded():
    _len = 20
    k = Keyframed(
        data={0:1, 15:2},
        n=_len,
    )
    assert k.is_bounded
    assert k.__len__() == _len
    assert list(k.keyframes) == [0,15] # last frame (19) isn't a keyframe
    assert k[0] == k[10] == 1
    assert k[15] == k[19] == 2
    with pytest.raises(StopIteration):
        k[20]

def test_data_bounded_truncated():
    k = Keyframed(
        data={0:1, 15:2},
        n=10,
    )
    with pytest.raises(StopIteration):
        k[10]


#########################################

def test_append_len():
    k0 = Keyframed()
    k1 = Keyframed()
    k0.set_length(10)
    k1.set_length(20)
    newlen = len(k0) + len(k1)
    k0.append(k1)
    assert len(k0) == newlen

def test_append_keyframes():
    k0 = Keyframed({3:2}, n=5)
    k1 = Keyframed({4:1}, n=6)
    k0.append(k1)
    assert len(k0) == 11
    assert list(k0.keyframes) == [0,3,5,9]


##########################################

def test_new_keyframe_datum():
    new_index = 5
    new_value = 3
    k = Keyframed()
    k[new_index] = new_value
    assert list(k.keyframes) == [0, new_index]

def test_new_keyframe_datum_w_interp():
    new_index = 5
    new_value = 3
    k = Keyframed()
    k[new_index] = new_value, 'linear'
    k[4*new_index] = 4*new_value
    assert k[2*new_index] == 2*new_value

def test_new_keyframe_interp():
    new_index = 5
    k = Keyframed()
    k[3*new_index] = 4
    k[new_index] = None, 'linear'
    for i in range(20):
        print(i, k[i])
    assert k[2*new_index] == 2

########################################

def test_add_scalar():
    k = Keyframed({3:5})
    assert k[0] == 0
    assert k[3] == 5
    assert k[4] == 5
    k+=1
    assert k[0] == 1
    assert k[3] == 6
    assert k[4] == 6

def test_add_keyframed():
    k = Keyframed(data={3:4, 5:8}, interp={3:'linear', 6:'previous'}, n=10)
    assert k[0]==0
    assert k[1]==0
    assert k[3]==4
    assert k[4]==6
    assert k[5]==8
    assert k[6]==8
    assert k[8]==8
    k2 = Keyframed(data={1:2, 8:1}, n=10)
    k+=k2
    assert list(k.keyframes) == [0,1,3,5,6,8]
    assert k[0]==0
    assert k[1]==2
    assert k[3]==6
    assert k[4]==8
    assert k[5]==10
    assert k[6]==10
    assert k[7]==10
    assert k[8]==9

def test_add_keyframed_interp():
    k = Keyframed(data={3:4, 5:8}, interp={3:'linear', 6:'previous'}, n=10)
    assert k[0]==0
    assert k[1]==0
    assert k[3]==4
    assert k[4]==6
    assert k[5]==8
    assert k[6]==8
    assert k[8]==8
    k2 = Keyframed(data={1:2, 8:1}, interp={7:'linear'}, n=10)
    k+=k2
    assert list(k.keyframes) == [0,1,3,5,6,7,8]
    assert k[0]==0
    assert k[1]==2
    assert k[3]==6
    assert k[4]==8
    assert k[5]==10
    assert k[6]==10
    #assert k[7]==9.5
    #ssert k[8]==9
    for i,v in enumerate(k): print(i,v)
    #for i,v in enumerate(k._interp.items()): print(i,v)
    assert False


def test_enumerate_bounded():
    k = Keyframed(data={3:4, 5:8}, interp={3:'linear', 6:'previous'}, n=10)
    for i,v in enumerate(k): print(i,v)


# # need to change behavior to make this a passing test
# def test_add_keyframed_unbounded():
#     k = Keyframed(data={3:4, 5:8}, interp={3:'linear', 6:'previous'})
#     assert k[0]==0
#     assert k[3]==4
#     assert k[4]==6
#     assert k[5]==8
#     assert k[6]==8
#     k2 = Keyframed(data={1:2, 8:1})
#     k+=k2
#     assert list(k.keyframes) == [0,1,3,5,6,8]
