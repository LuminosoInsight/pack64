'''
Pack64 is a vector encoding using a kind-of-floating-point, kind-of-base64
representation requiring only 3 bytes per vector entry.  This Python module
provides functions for encoding and decoding pack64 vectors.
'''

__all__ = ['pack64', 'unpack64']

import math
import numpy as np


# The characters used in encoding, in order; various derived lookup tables
CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
DIGIT_TO_CHAR = np.fromstring(CHARS, dtype=np.uint8)
CHAR_TO_DIGIT = np.full((128,), -1, dtype=np.int)
CHAR_TO_DIGIT[DIGIT_TO_CHAR] = np.arange(64)
VALID_CHARS = set(CHARS) | set(CHARS.encode('ascii'))

# The smallest positive number that cannot be encoded with a biased exponent of
# zero.  We determine the exponent by comparing the largest number in the
# vector with this one.  Note the offset of 0.5 due to rounding.
EPSILON = (2.0 ** 17 - 0.5) * 2.0 ** -40

# On rounding error: because we do not directly check that the packed values
# fit in 18 bits, a rounding error in calculating the exponent could cause a
# large error in the result.  Fortunately, this calculation should be exact
# despite using floating point arithmetic.  frexp() is exact, and the output
# should transition at EPSILON times powers of two, so it is sufficient to
# check that the input to frexp() is exact at these values.  Because all such
# values are a small integer times a power of two, they can be represented
# exactly and produce exact results when divided by EPSILON.

# On negative numbers: we never emit the string 'gAA', for -(2 ** 17).  Doing
# so would allow us to encode a small number of vectors with greater precision,
# but it doesn't seem worth the effort.


def pack64(vector):
    '''
    Encode the given vector, returning a string.  Accepts any object that can
    be converted to a NumPy float array.
    '''
    if not len(vector):
        return 'A'
    vector = np.asarray(vector)

    largest_entry = np.max(np.abs(vector))
    if not np.isfinite(largest_entry):
        raise ValueError('Vector contains an invalid value.')
    if not largest_entry:  # Remarkably, using == here is measurably slower
        biased_exponent = 0
    else:
        biased_exponent = max(math.frexp(float(largest_entry) / EPSILON)[1], 0)
        if biased_exponent > 63:
            raise OverflowError('Vector has an entry too large to encode.')

    values = np.round(vector * 0.5 ** (biased_exponent - 40)).astype(np.int)
    digits = np.empty((3 * len(values) + 1,), dtype=np.int)
    digits[0] = biased_exponent
    digits[1::3] = values >> 12
    digits[2::3] = values >> 6
    digits[3::3] = values
    digits &= 63
    return DIGIT_TO_CHAR[digits].tobytes().decode('ascii')


def unpack64(string, check=True):
    '''
    Decode the given string, returning a NumPy array of dtype float32.
    Optionally pass check=False to disable input validation, for circumstances
    where you are sure the input is a properly packed vector.
    '''
    if check and (len(string) % 3 != 1 or not VALID_CHARS.issuperset(string)):
        raise ValueError('Cannot decode string %r' % string)
    digits = CHAR_TO_DIGIT[np.fromstring(string, dtype=np.uint8)]
    values = (digits[1::3] << 12) + (digits[2::3] << 6) + digits[3::3]
    values -= (values >> 17) << 18
    return values.astype(np.float32) * 2.0 ** (digits[0] - 40)
