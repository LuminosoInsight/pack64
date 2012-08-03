pack64
======
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

If you wonder why you'd need this, the fact is that you might not. But at
Luminoso, we send *lots* of vectors over the network.

Specifications
==============

pack64
------

The `pack64` function returns a string *b* of bytes, representing digits using
the URL-safe base64 character set `(A-Z, a-z, 0-9, -, _)`, as follows:

* b[0] contains the power-of-two exponent, biased by 40. That is:

    - An exponent of 0 ("A") means to multiply all the integers that
      follow by 2^-40.
    - An exponent of 30 ("e") means to multiply the integers by 2^-10 (that is,
      divide them by 1024).
    - An exponent of 40 ("o") means to leave the integers as is.
    - An exponent of 63 ("_") means to multiply the integers by
      2^23.

  Call this number 2^(b[0] - 40) the *increment*.

* The increment is chosen to maximize precision. To choose the increment,
  find the number "a" such that 2^a is *larger* than all the magnitudes
  in the vector. The correct value for the increment is then 2^(a - 17).
  However, if this gives an increment lower than 2^-40, use 2^-40 instead.

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
  
The last value will be found in `b[3*K-2 : 3*K+1]`, so the length of the
string overall will be 3*K + 1.

This encoding can represent positive, negative, or zero values, with
magnitudes from 2^-40 to approximately 2^40, as long as the other
values in the vector are comparable in magnitude.

If the vector contains infinity, NaN, or an entry of magnitude 2^40 or
greater, this should raise a ValueError.

unpack64
--------
Unpacks a vector that has been encoded with the pack64 function.

Takes in a string of 3n+1 URL-safe base64 characters, and returns a
vector of length n, such that `unpack64(pack64(vec))` is equal
to `vec` within five significant digits of precision.
 
In Python, this returns a NumPy vector of dtype `np.float32`. In JavaScript, it
returns a standard array of numbers.

Precision
=========
Each entry in a pack64 vector is specified with 18 bits of precision. This is
3/4 of the precision of an IEEE 754 single-precision float, which has 24 bits
of precision.

The important difference is that every value in the vector is specified with
the same level of granularity. The exponent defines 2^18 possible values for
each entry, and every entry chooses from the *same* 2^18 values.

This will lose precision in entries of a vector that are much smaller than
other entries, possibly even rounding them to 0. However, when the larger
entries are accurately represented, the precision of the small entries matters
less.

License
=======
(c) 2012 Luminoso, LLC. pack64 is released as free software under the MIT
license. See LICENSE for the terms of the MIT license (there aren't many).

