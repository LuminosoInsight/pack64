from pack64 import pack64, unpack64
from csc_utils.vector import pack64_check as reference_pack64, unpack64 as reference_unpack64
import numpy as np

def test_random_vectors():
    for iter in xrange(800):
        magnitude = pow(2., (iter-500)/10.)
        length = (iter % 10) + 1
        vec = np.random.normal(size=(length,)) * magnitude
        try:
            reference_unpack64(reference_pack64(vec))
            yield encoding_check, vec
            yield decoding_check, vec
        except (OverflowError, ValueError):
            # this is a vector we can't encode in the original system
            pass

def encoding_check(vec):
    a = reference_pack64(vec)
    b = pack64(vec)
    assert a == b,\
            '%s should have encoded to %s, got %s' % (vec, a, b)

def decoding_check(vec):
    encoded = reference_pack64(vec)
    a = reference_unpack64(encoded)
    b = unpack64(encoded)
    assert np.allclose(a, b), '%s should have decoded to %s, got %s' % (encoded, a, b)

