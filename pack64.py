import numpy
import math

# reimplementation of Rob's numpy-array-packing thing.

#from csc_utils.vector import pack64, unpack64


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
        number += 262144 # that's 32*(64^2) + 2^17 = 2^18
    # integer-division
    first = number / 4096
    without_firstval = number - 4096 * first
    second = without_firstval / 64
    third = without_firstval - 64*second
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
    vector = numpy.asarray(vector)
    highest = max(numpy.abs(vector))
    if numpy.isinf(highest) or numpy.isnan(highest) or highest > 2**40:
        raise ValueError, 'Vector contains an invalid value.'
    if not highest:
        a = 0
    elif (not highest % 2) or \
         (highest < 2 and highest==2**int(math.log(highest,2))):
        # special case for powers of two
        a = int(math.log(highest, 2)) + 1
    else:
        a = int(math.ceil(math.log(highest, 2)))
    print highest, '<', 2**a
    exponent = max(a-17, -40)
    increment = 2**exponent
    first = exponent + 40
    newvector = vector / float(increment)
 #   newvector = newvector.astype('int') # is there a faster way?
    # TODO: use numpy operations to make this faster
    encoded = [twosComplementEncode(value) for value in newvector]
    return chars[first] + ''.join(encoded)


def unpack64(string):
    """
    Decode the given string (encoded from pack64) into a numpy array.
    See documentation in pack64_specs.txt.
    """
    increment = 2**(chars_to_indices[string[0]] - 40)
    numbers = numpy.array([chars_to_indices[s] for s in string[1:]])
    # highplace = numbers[::3]
    # midplace = numbers[1::3]
    # lowplace = numbers[2::3]
    values = 4096*numbers[::3] + 64*numbers[1::3] + numbers[2::3]
    # TODO: use numpy operations to make this faster
    values = [x if x<=131071 else x-262144 for x in values]
    return numpy.array(values) * increment
