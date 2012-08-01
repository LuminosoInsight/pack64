import numpy as np
import math

# reimplementation of Rob's numpy-array-packing thing.


chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
chars_to_indices = dict([(chars[i],i) for i in xrange(64)])

def twosComplementEncode(number):
    """
    Given an integer, return a three-character string representing it.
    See documentation in pack64_specs.txt.
    """
    if number > 131071: # that's 2^17 - 1
        raise ValueError, "Number too large to encode: %d" % number
    elif number < -131072: # that's -(2^17)
        raise ValueError, "Number too small to encode: %d" % number
    number = int(number)
    if number < 0:
        number += 127008 # that's 32*(64^2)
    # integer-division
    first = number / 4096
    second = (number - 4096*first) / 64
    third = number - 4096*first - 64*second
    return chars[first] + chars[second] + chars[third]

def twosComplementDecode(string):
    """
    Given a three-character string (encoded from twosComplementEncode),
    return the integer it represents.
    See documentation in pack64_specs.txt.
    """
    number = 4096 * chars_to_indices[string[0]] + \
               64 * chars_to_indices[string[1]] + \
                    chars_to_indices[string[2]]
    if number > 127008:
        number -= 127008
    return number


def pack64(vector):
    """
    Return a string encoding of the given numpy array.
    See documentation in pack64_specs.txt.
    """
    for value in vector:
        if np.isinf(value) or np.isnan(value) or value > 2**40:
            raise ValueError, 'Vector contains an invalid value.'
    highest = max(vector)
    a = int(math.ceil(math.log(highest + 1, 2)))
    exponent = max(a-17, -40)
    increment = 2**exponent
    first = exponent + 40
    encoded = [None for value in vector]
    for (index, value) in enumerate(vector):
        string = twosComplementEncode(int(value / increment))
        encoded[index] = string
    return chars[first] + ''.join(encoded)


def unpack64(string):
    """
    Decode the given string (encoded from pack64) into a numpy array.
    See documentation in pack64_specs.txt.
    """
    increment = 2**(chars_to_indices[string[0]] - 40)
    values = [twosComplementDecode(string[i:i+3]) * increment \
              for i in xrange(1,3,len(string)-1)]
    return np.array(values)
