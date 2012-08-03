"""
This file tests that our pack64 and unpack64 functions are compatible with the
versions in Commonsense Computing's csc_utils, which we often need to
interoperate with.

We reimplemented them from the specification to be sure that we could release
pack64/unpack64 under the MIT license.
"""

from pack64 import pack64, unpack64
from csc_utils.vector import pack64_check as reference_pack64, unpack64 as reference_unpack64
import numpy as np
import time

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

def test_specific_vectors():
    yield encoding_check, []
    yield decoding_check, []
    yield encoding_check, [0., 0., 0.]
    yield decoding_check, [0., 0., 0.]
    yield encoding_check, [-1.]
    yield decoding_check, [-1.]
    yield encoding_check, [1.]
    yield decoding_check, [1.]
    yield encoding_check, [1., 2.]
    yield decoding_check, [1., 2.]
    yield encoding_check, [.5, .25]
    yield decoding_check, [.5, .25]

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

def test_speed():
    vectors = [np.random.normal(size=(i%40+1,)) for i in xrange(40)]
    start1 = time.time()
    for vec in vectors:
        reference_unpack64(reference_pack64(vec))
    time_reference = (time.time() - start1)*1000
    start2 = time.time()
    for vec in vectors:
        unpack64(pack64(vec))
    time_ours = (time.time() - start2)*1000
    assert time_ours < time_reference,\
        "Took %4.4f ms. Time to beat: %4.4f ms." % (time_ours, time_reference)

