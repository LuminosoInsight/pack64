pack64
======
Pack64 is a vector encoding, with code for encoding and decoding in Python,
Ruby, and JavaScript.  It packs a vector into a kind-of-floating-point,
kind-of-base64 representation, requiring only 3 bytes per vector entry.

This is meant for transmitting vector data in situations where:

* Arbitrary bytes can't be transmitted
* We need to send the vector in as few bytes as possible
* Simply base64-encoding floating-point data -- at 5.33 bytes per entry --
  isn't small enough
* Some loss of precision is acceptable

Possible applications include transmitting a vector in a URL or JSON object.

If you wonder why you'd need this, the fact is that you might not.  But at
Luminoso, we send *lots* of vectors over the network.


Specifications
==============

pack64
------
Returns a string *b* of bytes, representing digits using the URL-safe base64
character set `(A-Z, a-z, 0-9, -, _)`, as follows:

* b[0] contains the power-of-two exponent, biased by 40.  That is:

    - An exponent of 0 ("A") means to multiply all the integers that follow by
      2^-40.
    - An exponent of 30 ("e") means to multiply the integers by 2^-10 (that is,
      divide them by 1024).
    - An exponent of 40 ("o") means to leave the integers as is.
    - An exponent of 63 ("_") means to multiply the integers by 2^23.

  Call this number 2^(b[0] - 40) the *increment*.

* The increment is chosen to maximize precision. To choose the increment, find
  the number "a" such that 2^a is *larger* than all the magnitudes in the
  vector.  The correct value for the increment is then 2^(a - 17).  However, if
  this gives an increment lower than 2^-40, use 2^-40 instead.  For example,
  the zero-length vector is encoded as `A`, and a length-two zero vector is
  encoded as `AAAAAAA`.

* b[1:4], b[4:7], etc. contain the values in the vector, as 18-bit,
  big-endian, twos-complement integers, which will all be multiplied by
  the increment. That is:

    - `AAA` represents 0.
    - `AAB` represents 1.
    - `AAC` represents 2.
    - `___` represents -1.
    - `__-` represents -2.
    - `f__` represents the highest possible value, (2^17 - 1).
    - `gAA` represents the lowest possible value, -(2^17).

The last value will be found in `b[3*K-2:3*K+1]`, so the length of the string
overall will be 3*K + 1.

This encoding can represent positive, negative, or zero values with magnitudes
from 2^-40 to approximately 2^40.  It cannot represent inf or nan, and encoders
should report an error when those are encountered; you probably don't want to
transmit them in a vector anyhow.  Encoders should likewise report an error if
they encounter values of magnitude 2^40 or greater.

unpack64
--------
Decodes a vector that has been encoded with pack64, returning an appropriate
data structure.  In Python, this returns a NumPy vector of dtype `np.float32`;
in JavaScript, it returns a standard array of numbers.


Precision
=========

The largest entry in a pack64 vector is specified with 17 bits of precision.
This is approximately 3/4 of the precision of an IEEE 754 single-precision
float (24 bits), and corresponds to five significant (decimal) digits.

Importantly, however, every value in the vector is specified with the same
*absolute* precision.  The exponent defines 2^18 possible values for each
entry, and each entry chooses from these *same* values.  Thus entries of a
vector that are much smaller than the largest entry will lose relative
precision, possibly even being rounded to zero.  However, for transmitting
mathematical vectors, the relative precision of smaller entries generally
matters less.


License
=======
(c) 2012-2016 Luminoso Technologies.  pack64 is released as free software under
the MIT license.  See LICENSE for the terms of the MIT license (there aren't
many).
