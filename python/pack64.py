'''
Pack64 is a vector encoding using a kind-of-floating-point, kind-of-base64
representation requiring only 3 bytes per vector entry.  This Python module
provides functions for encoding and decoding pack64 vectors.
'''

__all__ = ['pack64', 'unpack64']

import math
import numpy as np


# CHARS is a bytestring of the 64 characters in the encoding, in order.
CHARS = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'

# Make lookup tables for those characters.
# DIGIT_TO_CHAR maps the numbers 0-63 to those characters.
DIGIT_TO_CHAR = np.frombuffer(CHARS, dtype=np.uint8)

# CHAR_TO_DIGIT maps byte values of those characters to the numbers 0-63.
# Other byte values are mapped to -1, and do not appear in VALID_CHARS.
CHAR_TO_DIGIT = np.full((128,), -1, dtype=np.int)
CHAR_TO_DIGIT[DIGIT_TO_CHAR] = np.arange(64)
VALID_CHARS = set(CHARS)

# Compute a small value that we use in determining what the exponent should
# be (more on this in a moment):
EPSILON = (2.0 ** 17 - 0.5) * 2.0 ** -40

# EPSILON is used to determine the biased exponent emitted by pack64().  The
# largest integer part that can be emitted is (2 ** 17 - 1), and hence the
# largest number that can be emitted with a biased exponent of zero is
# (2 ** 17 - 1) * (2 ** -40).  However, numbers slightly larger than this still
# round down to this when encoded.  The smallest positive number that (rounded)
# requires a biased exponent of 1 is EPSILON.  By extension, the smallest
# number that requires a biased exponent of 2 is 2 * EPSILON, and so on.

# Thus, the biased exponent that should be used can be found by applying the
# following rule to the magnitude L of the largest vector entry:
#   If L is less than...            Set the biased exponent to ...
#     EPSILON                         0
#     2 * EPSILON                     1
#     4 * EPSILON                     2
#     ...                             ...
# Or, put another way:
#   If L / EPSILON is less than...  Set the biased exponent to...
#     1 (i.e. 2 ** 0)                 0
#     2 (i.e. 2 ** 1)                 1
#     4 (i.e. 2 ** 2)                 2
#     ...                             ...
# So the biased exponent should be the smallest nonnegative integer e such that
#     L / EPSILON == m * (2 ** e)
# with m < 1.  This is exactly the computation provided by math.frexp(),
# except that we have to handle "nonnegative" ourselves.

# Because we do not check directly that the packed values fit in 18 bits, a
# rounding error in this calculation could cause a large error in the result.
# Fortunately, the values of M where we need to transition between exponents
# are all power-of-two multiples of EPSILON, which are represented exactly and
# produce exact results when divided by EPSILON and passed to frexp().

# Finally, note that this calculation ignores the availablity of 'gAA' for
# -(2 ** 17).  Using this string would allow us to encode a small number of
# vectors with greater precision, but it doesn't seem worth the effort.


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
    if isinstance(string, bytes):
        bstring = string
    else:
        bstring = string.encode('ascii')

    if check and (len(bstring) % 3 != 1 or not VALID_CHARS.issuperset(bstring)):
        raise ValueError('Cannot decode string %r' % string)
    digits = CHAR_TO_DIGIT[np.frombuffer(bstring, dtype=np.uint8)]
    values = (digits[1::3] << 12) + (digits[2::3] << 6) + digits[3::3]
    values -= (values >> 17) << 18
    return values.astype(np.float32) * 2.0 ** (digits[0] - 40)
