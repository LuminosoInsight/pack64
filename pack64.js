/*
 * unpack64: decodes a pack64'd string into a vector.
 *
 * This function is for decoding a packed vector format, defined in the Python
 * package `pack64`.
 * 
 * The format uses URL-safe base64 to encode an exponent followed by several
 * 18-bit signed integers.
 */

base64_alphabet =
"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
base64_map = {};
for (var i=0; i<64; i++) {
    base64_map[base64_alphabet.charAt(i)] = i;
}

/* 2^17 is the number that makes an 18-bit signed integer go negative. */
SIGN_BIT = 131072;
ROUND_MARGIN = SIGN_BIT / (SIGN_BIT - 0.5);

function unpack64(str) {
    var hexes = [];
    for (var i=0; i<str.length; i++) {
        hexes[i] = base64_map[str.charAt(i)];
    }
    var vector = [];
    var K = (hexes.length-1)/3;
    var unit = Math.pow(2, hexes[0] - 40);
    for (var i=0; i<K; i++) {
        var integer = hexes[i*3 + 1]*4096 + hexes[i*3+2]*64 + hexes[i*3+3];
        if (integer >= SIGN_BIT) integer -= SIGN_BIT*2;
        vector[i] = integer * unit;
    }
    return vector;
}

function pack64(vec) {
  // Calculate the smallest power of 2 we *don't* need to represent.
  // The exponent we want will be 17 lower than that.
  var max = 0, i;
  for (i=0; i<vec.length; i++)
    if (Math.abs(vec[i]) > max) max=Math.abs(vec[i] * ROUND_MARGIN);
  var upperBound = Math.floor(1 + Math.log(max)/Math.log(2));
  var exponent = upperBound - 17;
  if (exponent > 23)
    // Overflow. Return the flag vector for "almost infinity".
    return '-';
  if (exponent < -40)
    // Underflow. Lose some precision. Or maybe all of it.
    exponent = -40;

  var power = Math.pow(2, exponent);
  var res = [base64_alphabet[exponent+40]];
  for (i=0; i<vec.length; i++) {
    var num = Math.round(vec[i]/power);
    if (num < 0) num += SIGN_BIT*2;
    // Do the signed arithmetic to represent an 18-bit integer.
    res.push(base64_alphabet[(num % (1 << 18)) >> 12]);
    res.push(base64_alphabet[(num % (1 << 12)) >> 6]);
    res.push(base64_alphabet[num % (1 << 6)]);
  }
  return res.join('');
}
