import numpy as np
import math

# reimplementation of Rob's numpy-array-packing thing.


chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
chars_to_indices = dict([(chars[i],i) for i in xrange(64)])

def twosComplementEncode(number):
    """
    Given a number, return a three-character string representing
    (the integer part of) it.
    See documentation in pack64_specs.txt.
    """
    if number > 131071: # that's 2^17 - 1
        raise ValueError, "Number too large to encode: %d" % number
    elif number < -131072: # that's -(2^17)
        raise ValueError, "Number too small to encode: %d" % number
    number = int(number)
    if number < 0:
        number += 262144 # that's 32*(64^2) + 2^17
    # integer-division
    first = number / 4096
    firstval = 4096 * first
    second = firstval / 64
    third = firstval - 64*second
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
    if number > 131071:
        number -= 262144
    return number


def pack64(vector):
    """
    Return a string encoding of the given numpy array.
    See documentation in pack64_specs.txt.
    """
    highest = max(vector)
    if np.isinf(highest) or np.isnan(highest) or highest > 2**40:
        raise ValueError, 'Vector contains an invalid value.'
    a = int(math.ceil(math.log(highest + 1, 2)))
    exponent = max(a-17, -40)
    increment = 2**exponent
    first = exponent + 40
    vector /= float(increment)
    # TODO: use np operations to make this faster
    encoded = [twosComplementEncode(value) for value in vector]
    return chars[first] + ''.join(encoded)


def unpack64(string):
    """
    Decode the given string (encoded from pack64) into a np array.
    See documentation in pack64_specs.txt.
    """
    increment = 2**(chars_to_indices[string[0]] - 40)
    numbers = np.array([chars_to_indices[s] for s in string[1:]])
    highplace = numbers[::3]
    midplace = numbers[1::3]
    lowplace = numbers[2::3]
    values = 4096*highplace + 64*midplace + lowplace
    # TODO: use np operations to make this faster
    values = [x if x<=131071 else x-262144 for x in values]
    return np.array(values) * increment
