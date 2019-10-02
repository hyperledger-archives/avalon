  /*****************************************************************************
  * Copyright 2019 iExec Blockchain Tech
  *
  * Licensed under the Apache License, Version 2.0 (the "License");
  * you may not use this file except in compliance with the License.
  * You may obtain a copy of the License at
  *
  *     http://www.apache.org/licenses/LICENSE-2.0
  *
  * Unless required by applicable law or agreed to in writing, software
  * distributed under the License is distributed on an "AS IS" BASIS,
  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  * See the License for the specific language governing permissions and
  * limitations under the License.
  *****************************************************************************/
package org.eea.tcf.worker.utils;

import org.web3j.utils.Numeric;

import javax.xml.bind.DatatypeConverter;
import java.util.ArrayList;
import java.util.List;

public class BytesUtils {

    // "0x0000000000000000000000000000000000000000"
    public final static String EMPTY_ADDRESS =
            BytesUtils.bytesToString(new byte[20]);

    //"0x0000000000000000000000000000000000000000000000000000000000000000"
    public final static String EMPTY_HEXASTRING_64 =
            BytesUtils.bytesToString(new byte[32]);
    private BytesUtils() {
        throw new UnsupportedOperationException();
    }

    public static String bytesToString(byte[] bytes) {
        return Numeric.toHexString(bytes);
    }

    public static String[] bytesToStrings(List<byte[]> bytes) {
        String strings[] = new String[bytes.size()];

        for(int i = 0; i <  bytes.size(); i++)
            strings[i] = bytesToString(bytes.get(i));

        return strings;
    }

    public static byte[] stringToBytes(String hexaString) {
        return Numeric.hexStringToByteArray(hexaString);
    }

    public static List<byte[]> stringsToBytes(String... strings) {
        List<byte[]> bytes = new ArrayList<byte[]>();

        for(String s: strings) {
            bytes.add(stringToBytes(s));
        }

        return bytes;
    }

    public static String hexStringToAscii(String hexString) {
        return new String(DatatypeConverter.parseHexBinary(Numeric.cleanHexPrefix(hexString)));
    }

    public static boolean isHexaString(String hexaString) {
        // \\p{XDigit} matches any hexadecimal character
        return Numeric.cleanHexPrefix(hexaString).matches("\\p{XDigit}+");
    }

    public static boolean isBytes32(byte[] bytes){
        return bytes != null && bytes.length == 32;
    }

    // this adds zeros to the left of the hex string to make it bytes32
    public static byte[] stringToBytes32(String hexString) {
        byte[] stringBytes = stringToBytes(hexString);
        if (isBytes32(stringBytes)) return stringBytes;

        String cleanString = Numeric.cleanHexPrefix(hexString);
        String padded = padRight(cleanString, 64 - cleanString.length());
        return Numeric.hexStringToByteArray(padded);
    }

    public static List<byte[]> stringsToBytes32(String... strings) {
        List<byte[]> bytes = new ArrayList<byte[]>();

        for(String s: strings) {
            bytes.add(stringToBytes32(s));
        }

        return bytes;
    }

    public static String padRight(String s, int n) {
        if (n <= 0) return s;
        String zeros = new String(new char[n]).replace('\0', '0');
        return s + zeros;
    }

    public static boolean compareBytes(byte[] left, byte[] right, int length,
                                       int leftPadding, int rightPadding) {
        boolean same = true;
        // padding refers to the right argument

        for(int i = 0; i < length; i++)
            same = same && left[i + leftPadding] == right[i+rightPadding];

        return same;
    }

    public static boolean compareBytes(byte[] left, byte[] right, int nBytes) {
        return compareBytes(left, right, nBytes, 0, 0);
    }

    public static boolean compareBytes(byte[] left, byte[] right,
                                       int leftPadding, int rightPadding) {
        int length = Math.max(left.length, right.length);
        return compareBytes(left, right, length, leftPadding, rightPadding);
    }

    public static boolean compareBytes(byte[] left, byte[] right) {
        return compareBytes(left, right, Math.max(left.length, right.length));
    }
}
