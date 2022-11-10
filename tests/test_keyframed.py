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

def test_append_len():
    k0 = Keyframed()
    k1 = Keyframed()
    k0.set_length(10)
    k1.set_length(20)
    newlen = len(k0) + len(k1)
    k0.append(k1)
    assert len(k0) == newlen

