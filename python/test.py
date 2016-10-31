from __future__ import unicode_literals

import numpy as np
from nose.tools import assert_raises, eq_

from pack64 import pack64, unpack64


def _check(vector, expected=None, exact=False):
    # Checks that the given vector:
    #   * Encodes successfully (and to a particular string, if specified)
    #   * Decodes successfully to exactly the same value (if specified) or to
    #     within the expected tolerance (see below for what this tolerance is)
    #   * Produces exactly the same string when the decoded value is reencoded
    # Returns the maximum absolute deviation between the given and decoded
    # vectors, and the tolerance to which it was compared.
    encoded = pack64(vector)
    if expected is not None:
        eq_(encoded, expected)
    decoded = unpack64(encoded)
    eq_(pack64(decoded), encoded)

    if not len(vector):
        deviation = 0.0
    else:
        deviation = np.max(np.abs(decoded - vector))
    if exact:
        tolerance = 0.0
    else:
        # Generally pack64 guarantees a precision of 2 ** -17 times the largest
        # magnitude entry.  However, we have to adjust for two details.
        #   * The largest magnitude entry may be rounded for packing in such a
        #     way that the precision is slightly less than that guarantee.
        #   * The smallest positive number that can be packed at all is
        #     2 ** -40, so the absolute precision available for very small
        #     vectors, regardless of the size of the vector, is 2 ** -41.
        tolerance = max(np.max(np.abs(vector)) / (2.0 ** 17 - 0.5), 2.0 ** -41)
    assert deviation <= tolerance
    return deviation, tolerance


def test_specific_vectors():
    # Check small integers times a power of two, which can be encoded exactly
    _check([], expected='A', exact=True)
    _check([0.0], expected='AAAA', exact=True)
    _check([1.0], expected='YQAA', exact=True)
    _check([-1.0, 1.0], expected='YwAAQAA', exact=True)
    _check([2.0, 4.0], expected='aIAAQAA', exact=True)
    _check([0.25, 0.5], expected='XIAAQAA', exact=True)

    # Check rounding behavior
    _check([2.0 ** 17 - 1.0], expected='of__', exact=True)
    _check([2.0 ** 17], expected='pQAA', exact=True)
    _check([2.0 ** 17 - 0.6], expected='of__')  # Rounds down
    _check([2.0 ** 17 - 0.4], expected='pQAA')  # Rounds up
    _check([2.0 ** 17 - 0.5], expected='pQAA')  # Rounds up towards even
    _check([2.0 ** 17 - 1.5], expected='of_-')  # Rounds down towards even
    _check([2.0 ** -50], 'AAAA')  # Rounds to zero, does not crash

    # Demonstrate vectors at the edge of exact representability
    _check([2.0 ** 16, -1.0], expected='oQAA___', exact=True)
    _check([2.0 ** 17, -1.0], expected='pQAAAAA')  # -1.0 rounds towards zero
    _check([2.0 ** 17, -1.5], expected='pQAA___')  # -1.5 rounds towards -2.0

    # Demonstrate a vector that could be encoded exactly as 'XgAAAAB' but isn't
    _check([-1.0, 2.0 ** -17], expected='YwAAAAA')

    # Check for any intermediate truncation which would cause misencoding
    _check([2.0 ** 16 + 0.5001], expected='oQAB')
    _check([np.float32(2.0 ** 16 + 0.5001)], expected='oQAA')

    # Show that the tolerance used by the test code is as tight as possible
    # The maximum possible deviation in the absence of underflow
    deviation, tolerance = _check([2.0 ** 17 - 0.5, 1.0], expected='pQAAAAA')
    eq_(deviation, tolerance)
    # The maximum possible deviation caused by underflow
    deviation, tolerance = _check([2.0 ** -41], expected='AAAA')
    eq_(deviation, tolerance)


def test_input_types():
    # Both strings and bytestrings are unpackable
    assert np.all(unpack64('abcd') == unpack64(b'abcd'))

    # Anything that can be converted to a NumPy array is packable
    eq_(pack64([1.0, 2.0]), 'ZIAAQAA')
    eq_(pack64((1.0, 2.0)), 'ZIAAQAA')
    eq_(pack64(np.array([1.0, 2.0], dtype=np.float32)), 'ZIAAQAA')
    eq_(pack64(np.array([1.0, 2.0], dtype=np.float64)), 'ZIAAQAA')
    eq_(pack64(np.array([1.0, 2.0], dtype=np.int32)), 'ZIAAQAA')


def test_errors():
    # Nonfinite values are rejected
    for value in (float('inf'), float('nan')):
        with assert_raises(ValueError):
            pack64([value])

    # Out of range values are rejected; check near the edge of the range
    with assert_raises(OverflowError):
        pack64([(2.0 ** 17 - 0.5) * 2.0 ** 23])
    _check([(2.0 ** 17 - 0.6) * 2.0 ** 23], expected='_f__')
    with assert_raises(OverflowError):
        # (This could actually be encoded as '_gAA'.)
        pack64([-(2.0 ** 17 - 0.5) * 2.0 ** 23])
    _check([-(2.0 ** 17 - 0.6) * 2.0 ** 23], expected='_gAB')

    # Strings with bad lengths or characters are rejected
    for string in ('', 'xx', b'xx', '\U0001f43c', 'Hey!', 'panda', 'rutabaga'):
        with assert_raises(ValueError):
            unpack64(string)

    # Some (but not all) bad strings are accepted if error checking is disabled
    for string in ('xx', 'Hey!', 'panda'):
        unpack64(string, check=False)
    with assert_raises(ValueError):
        unpack64('rutabaga', check=False)


def test_random_vectors():
    for magnitude in range(-45, 45):
        scale = 2.0 ** magnitude
        for length in range(1, 52, 5):
            vec = np.random.normal(scale=scale, size=(length,))
            # As demonstrated above, this is the range of encodable values
            if np.max(np.abs(vec)) < (2.0 ** 17 - 0.5) * 2.0 ** 23:
                _check(vec)
