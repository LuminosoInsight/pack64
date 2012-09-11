"""
Pack64 is a vector encoding, with code for encoding and decoding it in Python
and JavaScript. It packs a vector into a kind-of-floating-point, kind-of-base64
representation, requiring only 3 bytes per vector entry.

This is meant for transmitting vector data over a network, in a situation
where:

* Arbitrary bytes can't be transmitted
* We need to send the vector in as few bytes as possible
* Simply base64-encoding floating-point data -- at 5.33 bytes per entry --
  isn't small enough
* A loss of precision is acceptable, as long as the properties of the vector
  remain the same

Possible applications include rapidly updating a vector using STOMP, or
encoding a vector in a URL.
"""

import numpy
import math

chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
base64_array = numpy.chararray((64,), buffer=chars)
chars_to_indices = dict([(chars[i], i) for i in xrange(64)])

# This constant is 2^17, the value that represents the sign in an 18-bit two's
# complement encoding. The minimum integer that can be represented in such an
# encoding is -SIGN_BIT, and the maximum is SIGN_BIT - 1.
SIGN_BIT = 131072
ROUND_MARGIN = SIGN_BIT/(SIGN_BIT-0.5)
def twosComplementEncode(number, rounded=True):
    """
    Given a number, return a three-character string representing
    it (rounded to the nearest int), as 18-bit two's complement.

    When `rounded` is True (default), this rounds to the nearest integer to
    maximize precision. When `rounded` is False, it truncates for compatibility
    with previous versions.

    This function is not used by pack64; pack64 does a faster in-place version
    that is equivalent.

    See documentation in pack64/README.markdown.
    """
    if rounded:
        number = int(numpy.round(number))
    else:
        number = int(number)
    assert -SIGN_BIT <= number < SIGN_BIT, "Integer out of range: %d" % number
    if number < 0:
        number += SIGN_BIT * 2
    
    # using // for forward-compatible integer division
    first = number // 4096
    without_firstval = number - 4096 * first
    second = without_firstval // 64
    third = without_firstval - 64*second
    return chars[first] + chars[second] + chars[third]

def twosComplementDecode(string):
    """
    Given a three-character string (encoded from twosComplementEncode),
    return the integer it represents.
    
    See documentation in pack64/README.markdown.
    """
    number = 4096 * chars_to_indices[string[0]] + \
               64 * chars_to_indices[string[1]] + \
                    chars_to_indices[string[2]]
    if number >= SIGN_BIT:
        number -= SIGN_BIT*2
    return number

def pack64(vector, rounded=True):
    """
    Returns a compact string encoding that approximates the given NumPy
    vector. See the documentation in pack64/README.markdown.
    
    When `rounded` is True (default), this rounds to the nearest representable
    value, to maximize precision. When `rounded` is False, it truncates, for
    compatibility with previous versions.
    """
    vector = numpy.asarray(vector)
    if not len(vector):
        return 'A'
    highest = max(numpy.abs(vector))
    if rounded:
        # If we're going to round off integers, we must take into account the
        # case where we might round up to a power of 2.
        highest *= ROUND_MARGIN
    if numpy.isinf(highest) or numpy.isnan(highest):
        raise ValueError, 'Vector contains an invalid value.'
    if not highest:
        lowest_unused_power = -40
    else:
        lowest_unused_power = int(math.floor(numpy.log2(highest))) + 1
        if lowest_unused_power > 40:
            raise OverflowError
    exponent = max(lowest_unused_power-17, -40)
    increment = 2**exponent
    first = exponent + 40
    if rounded:
        newvector = numpy.round(vector / float(increment)).astype(numpy.int)
    else:
        newvector = (vector / float(increment)).astype(numpy.int)
    
    # do the two's complement encoding in place, across the entire vector
    length = 3*len(newvector) + 1
    digits = numpy.zeros((length,)).astype(numpy.int)
    digits[0] = first
    digits[1::3] = (newvector >> 12) % 64
    digits[2::3] = (newvector >> 6) % 64
    digits[3::3] = (newvector % 64)

    encoded = base64_array[digits]
    return encoded.tostring()

def unpack64(string):
    """
    Decode the given string (encoded from pack64) into a numpy array
    of type `numpy.float32`.
    
    See documentation in pack64/README.markdown.
    """
    increment = 2**(chars_to_indices[string[0]] - 40)
    numbers = numpy.array([chars_to_indices[s] for s in string[1:]])
    highplace = numbers[::3]
    midplace = numbers[1::3]
    lowplace = numbers[2::3]
    values = 4096*highplace + 64*midplace + lowplace
    signs = (values >= SIGN_BIT)
    values -= 2 * signs * SIGN_BIT
    return numpy.array(values, dtype=numpy.float32) * increment
