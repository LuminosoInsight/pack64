from pack64 import pack64, unpack64
import numpy as np

def test_random_vectors():
    for iter in xrange(900):
        magnitude = pow(2., (iter-500)/10.)
        length = (iter % 10) + 1
        vec = np.random.normal(size=(length,)) * magnitude
        if np.max(np.abs(vec)) < 2**40:
            yield round_trip_check, vec

def test_specific_vectors():
    yield round_trip_check, []
    yield round_trip_check, [0., 0., 0.]
    yield round_trip_check, [-1.]
    yield round_trip_check, [1.]
    yield round_trip_check, [1., 2.]
    yield round_trip_check, [.5, .25]

def test_encoding():
    assert pack64([]) == 'A'
    assert pack64([0.]) == 'AAAA'
    assert pack64([1.]) == 'YQAA'
    assert pack64([-1., 1.]) == 'YwAAQAA'
    assert pack64([2.**16, -1.]) == 'oQAA___'
    assert pack64([2.**20, -1.]) == 'sQAAAAA'

def round_trip_check(vec):
    newvec = unpack64(pack64(vec, round=True))
    if len(vec) == 0:
        precision = 0.
        maxdiff = 0.
    else:
        precision = np.max(np.abs(vec)) * (2**-17) + 2**-40
        maxdiff = np.max(np.abs(newvec - vec))
    assert np.allclose(newvec, vec, 1e-10, precision),\
        "%s isn't close enough to %s; difference=%s, precision=%s" % (newvec,
                vec, maxdiff, precision)

