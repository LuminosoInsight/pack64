package com.luminoso.pack64;

import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.*;

/**
 *  Pack64Test
 *
 *  <P> Junit test for the Java version of the Pack64 conversion
 *
 *  <P> This tests both the pack and unpack methods
 *
 *  <P> Sample Commandline:
 *  set CLASSPATH=.:./src:./test:./junit-4.13-beta-3.jar:./hamcrest-2.1.jar
 *  export CLASSPATH
 *  java com.luminoso.pack64/Pack64Test
 *
 */

public class Pack64Test {

    @Before
    public void setUp() {

    }

    @Test
    public void testPack64() {
        assertPackedEquals(new double[]{}, "A");
        assertPackedEquals(new double[]{0.0}, "AAAA");
        assertPackedEquals(new double[]{1.0}, "YQAA");
        assertPackedEquals(new double[]{-1.0, 1.0}, "YwAAQAA");

        assertPackedEquals(new double[]{Math.pow(2, 16), -1.0}, "oQAA___");
        assertPackedEquals(new double[]{Math.pow(2, 16),Math.pow(2, 17) - 1.0}, "oQAAf__");
        assertPackedEquals(new double[]{Math.pow(2, 16),Math.pow(2, 17) - 0.2}, "pIAAQAA");
        assertPackedEquals(new double[]{Math.pow(2, 16), Math.pow(-2, 17) + 0.2}, "pIAAwAA");
        assertPackedEquals(new double[]{Math.pow(2, 20), -1.0}, "sQAAAAA");
    }

    @Test
    public void testRoundTrip() {
        assertRoundtripIsEqual(new double[]{1.0, 2.0, 3.0});
        assertRoundtripIsEqual(new double[]{});
        assertRoundtripIsEqual(new double[]{0.0, 0.0, 0.0});
        assertRoundtripIsEqual(new double[]{-1});
        assertRoundtripIsEqual(new double[]{1});
        assertRoundtripIsEqual(new double[]{1, 2});
        assertRoundtripIsEqual(new double[]{0.5, 0.25});
    }

    private void assertPackedEquals(double[] vector, String compare) {
        assertEquals(Pack64.pack(vector),compare);
    }
    
    private String vectToString(double[] vector) {
        StringBuffer stRet = new StringBuffer();
        for (int i=0;i<vector.length-1;i++)
            stRet.append(vector[i]+",");

        // print the last value without the comma
        if (vector.length>0)
            stRet.append(vector[vector.length-1]);
        return stRet.toString();
    }

    private void assertRoundtripIsEqual(double[] vector) {
        double[] roundtripped = Pack64.unpack(Pack64.pack(vector));
        for (int i = 0; i < roundtripped.length; i++) {
            assertEquals("index="+i+" pack(unpack([" + vector[i] + "])) == [" + roundtripped[i] + "]",
            roundtripped[i],vector[i],0.0);
        }
    }  

    public static void main(String args[]) {
        org.junit.runner.JUnitCore.main("com.luminoso.pack64.Pack64Test");
    }
}