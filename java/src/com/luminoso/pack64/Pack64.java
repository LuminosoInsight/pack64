package com.luminoso.pack64;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

/**
 * pack64.pack: encodes a vector into a pack64'd string.
 * pack64.unpack: decodes a pack64'd string into a vector.
 *
 * This library is for decoding a packed vector format, defined originally
 * in the Python package `pack64`.
 * 
 * The format uses URL-safe base64 to encode an exponent followed by several
 * 18-bit signed integers.
 *
 * @copyright
 * (c) Copyright 2019 Luminoso Technologies, Inc
 * 
 * @license
 * MIT License - See LICENSE file
 * 
 */

public class Pack64 {

    // 2^17 is the number that makes an 18-bit signed integer go negative.
    static int SIGN_BIT = 131072;
    static Double ROUND_MARGIN = SIGN_BIT / (SIGN_BIT - 0.5);

    static char[] alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_".toCharArray();
    private static final Map<Character,Integer> alphabet_map;
    static {
        Map<Character, Integer> aMap = new HashMap<Character,Integer>();
        int i;
        for (i=0;i<alphabet.length;i++) {
            aMap.put(alphabet[i],i);
        }
        alphabet_map = Collections.unmodifiableMap(aMap);
    }

    /**
     * pack
     * @param double[] an arraby of doubles that make up the vector
     *
     * @return Returns an url save base64 string that represents the vector
     */
    public static String pack(double[] vector) {
        if (vector.length==0)
            return "A";

        // Calculate the smallest power of 2 we *don't* need to represent.
        // The exponent we want will be 17 lower than that.
        double max = 0;
        int i;
        for (i = 0; i < vector.length; i++) {
            double v = Math.abs(vector[i]) * ROUND_MARGIN;
            if (v > max) {
                max = v;
            }
        }

        int upperBound;
        if (max==0)
            upperBound = -40;
        else
            upperBound = (int) Math.floor(1 + Math.log(max) / Math.log(2));

        int exponent = upperBound - 17;
        if (exponent > 23) {
            // Overflow. Return the flag vector for "almost infinity".
            return String.valueOf('-');
        }

        if (exponent < -40) {
            // Underflow. Lose some precision. Or maybe all of it.
            exponent = -40;
        }

        double power = Math.pow(2, exponent);

        StringBuilder res = new StringBuilder();
        res.append(alphabet[exponent + 40]);

        for (i = 0; i < vector.length; i++) {
            int num = (int) Math.round((vector[i] / power));
            if (num < 0) {
                num += SIGN_BIT*2;
            }
            // Do the signed arithmetic to represent an 18-bit integer.
            res.append(alphabet[(num % (1 << 18)) >> 12]);
            res.append(alphabet[(num % (1 << 12)) >> 6]);
            res.append(alphabet[num % (1 << 6)]);
        }

        return res.toString();
    }

    /**
     * unpack
     *
     * @param String a base64 representation of a vector created with pack
     *
     * @return an array of double values representing the vector
     */
    public static double[] unpack(String stVect) {
        ArrayList<Integer> hexes = new ArrayList<Integer>();
        int i;
        for (i = 0; i < stVect.length(); i++) {
            hexes.add(alphabet_map.get(stVect.charAt(i)));
        }

        int K = (hexes.size() - 1) / 3;
        double[] vector = new double[K];
        double unit = Math.pow(2, hexes.get(0) - 40);
        for (i = 0; i < K; i++) {
            int base = i * 3;
            int integer = 4096*hexes.get(base + 1) + 64*hexes.get(base + 2) + hexes.get(base + 3);
            if (integer >= SIGN_BIT) {
                integer -= SIGN_BIT * 2;
            }
            vector[i] = (integer * unit);
        }

        return vector;
    }
}