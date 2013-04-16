# Pack64 is an encoding of vectors as strings. It packs a vector into a
# kind-of-floating-point, kind-of-base64 representation, requiring only
# 3 bytes per vector entry.
#
# See README.markdown for more details on the format.
#
# This Ruby gem provides support for Pack64 to Ruby. Strings get a method
# called .unpack64, which converts them into a Vector. Arrays and Vectors
# get .pack64 which turns them into a Pack64 string.
require 'matrix'

module Pack64
  CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
  SIGN_BIT = 131072
  ROUND_MARGIN = SIGN_BIT / (SIGN_BIT - 0.5)
  INFINITY = +1.0/0.0
  NAN = 0.0/0.0

  $chars_to_indices = {}

  CHARS.split('').each_with_index do |char, i|
    $chars_to_indices[char] = i
  end

  # Returns a compact string encoding that approximates an N-dimensional vector.
  # Can take in either a Vector or a standard array.
  def Pack64.pack64(vector)
    array = vector.to_a
    return 'A' if array.length == 0
    absolute = array.map { |x| x.abs }
    highest = absolute.max * ROUND_MARGIN
    if highest.infinite? or highest.nan?
      fail FloatDomainError.new('Vector contains an invalid value')
    end

    if highest == 0
      lowest_unused_power = -40
    else
      lowest_unused_power = Pack64.log2(highest).floor + 1
      if lowest_unused_power > 40
        fail RangeError.new('Overflow')
      end
    end

    exponent = [lowest_unused_power - 17, -40].max
    increment = 2**exponent
    first = exponent + 40
    newarray = array.map { |x| (x / (increment.to_f)).round }

    chunks = [CHARS[first]] + newarray.map { |x| Pack64.twos_complement_encode(x) }
    return chunks.join('')
  end

  # Decode the given string (encoded using pack64) into a Vector.
  def Pack64.unpack64(string)
    increment = 2**($chars_to_indices[string[0]] - 40).to_f
    rest = string[1..-1]
    numbers = []
    0.upto(rest.length / 3 - 1) do |index|
      chunk = rest[(index * 3)...(index * 3 + 3)]
      val = Pack64.twos_complement_decode(chunk)
      numbers.push(val * increment)
    end
    return Vector.elements(numbers)
  end

private

  def Pack64.log2(num)
    return Math.log(num) / Math.log(2)
  end

  # Given a number, return a three-character string representing it
  # (rounded to the nearest int), as 18-bit two's complement in base64.
  def Pack64.twos_complement_encode(number)
    number = number.round
    if number < -SIGN_BIT || number >= SIGN_BIT
      fail RangeError.new("Integer out of range: #{number}")
    end

    number += SIGN_BIT * 2 if number < 0

    first = number / 4096
    without_firstval = number - 4096 * first
    second = without_firstval / 64
    third = without_firstval - 64 * second
    return CHARS[first] + CHARS[second] + CHARS[third]
  end

  # Given a three-character string (encoded from twosComplementEncode),
  # return the integer it represents.
  def Pack64.twos_complement_decode(string)
    number = 4096 * $chars_to_indices[string[0]] \
             + 64 * $chars_to_indices[string[1]] \
             +      $chars_to_indices[string[2]]
    if number >= SIGN_BIT
      number -= SIGN_BIT * 2
    end
    number
  end

end

# Now include pack64 and unpack64 as methods of Strings, Vectors, and Arrays.
class String
  def unpack64
    Pack64.unpack64(self)
  end
end

class Vector
  def pack64
    Pack64.pack64(self)
  end
end

class Array
  def pack64
    Pack64.pack64(self)
  end
end

