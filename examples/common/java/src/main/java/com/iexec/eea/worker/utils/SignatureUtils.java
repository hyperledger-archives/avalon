package com.iexec.eea.worker.utils;

import org.web3j.crypto.*;
import org.web3j.utils.Numeric;

import java.math.BigInteger;
import java.security.SignatureException;

import com.iexec.eea.worker.security.Signature;

public class SignatureUtils {

    public static final Signature EMPTY_SIGNATURE =  new Signature();

    private SignatureUtils() {
        throw new UnsupportedOperationException();
    }

    public static boolean doesSignatureMatchesAddress(byte[] signatureR,
                                                      byte[] signatureS,
                                                      String hashToCheck,
                                                      String signerAddress){
        // check that the public address of the signer can be found
        for (int i = 0; i < 4; i++) {
            BigInteger publicKey = Sign.recoverFromSignature((byte) i,
                    new ECDSASignature(
                            new BigInteger(1, signatureR),
                            new BigInteger(1, signatureS)),
                    BytesUtils.stringToBytes(hashToCheck));

            if (publicKey != null) {
                String addressRecovered = "0x" + Keys.getAddress(publicKey);

                if (addressRecovered.equals(signerAddress)) {
                    return true;
                }
            }
        }

        return false;
    }

    public static boolean isSignatureValid(byte[] message, Signature sign, String signerAddress) {
        BigInteger publicKey = null;
        Sign.SignatureData signatureData = new Sign.SignatureData(sign.getV(), sign.getR(), sign.getS());

        try {
            publicKey = Sign.signedPrefixedMessageToKey(message, signatureData);
        } catch (SignatureException e) {
            e.printStackTrace();
            return false;
        }

        if (publicKey == null) return false;

        String addressRecovered = "0x" + Keys.getAddress(publicKey);
        return addressRecovered.equalsIgnoreCase(signerAddress);
    }

    public static Signature hashAndSign(String stringToSign, String walletAddress, ECKeyPair ecKeyPair) {
        byte[] message = Hash.sha3(BytesUtils.stringToBytes(stringToSign));
        Sign.SignatureData sign = Sign.signMessage(message, ecKeyPair, false);

        return new Signature(sign.getR(), sign.getS(), sign.getV());
    }

    public static String hashAndSignAsString(String stringToSign, ECKeyPair ecKeyPair) {
        byte[] message = Hash.sha3(BytesUtils.stringToBytes(stringToSign));
        Sign.SignatureData sign = Sign.signMessage(message, ecKeyPair, false);
        return createStringFromSignature(sign);
    }

    public static String signAsString(String stringToSign, ECKeyPair ecKeyPair) {
        byte[] message = Numeric.hexStringToByteArray(stringToSign);
        Sign.SignatureData sign = Sign.signMessage(message, ecKeyPair, false);
        return createStringFromSignature(sign);
    }

    public static Signature emptySignature() {
        return new Signature (
            BytesUtils.stringToBytes(BytesUtils.EMPTY_HEXASTRING_64),
            BytesUtils.stringToBytes(BytesUtils.EMPTY_HEXASTRING_64),
            BytesUtils.stringToBytes(BytesUtils.EMPTY_HEXASTRING_64)
        );

    }

    private static String createStringFromSignature(Sign.SignatureData sign) {
        String r = Numeric.toHexString(sign.getR());
        String s = Numeric.toHexString(sign.getS());
        String v = Numeric.toHexString(sign.getV());
        return String.join("", r, Numeric.cleanHexPrefix(s), v);
    }

}
