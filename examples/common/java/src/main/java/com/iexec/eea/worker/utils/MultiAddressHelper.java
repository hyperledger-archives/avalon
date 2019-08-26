package com.iexec.eea.worker.utils;

import io.ipfs.multiaddr.MultiAddress;
import org.web3j.utils.Numeric;

public class MultiAddressHelper {

    private static final String IPFS_GATEWAY_URI = "https://gateway.ipfs.io";

    private MultiAddressHelper() {
        throw new UnsupportedOperationException();
    }

    public static String convertToURI(String hexaString) {
        // Currently, only the IPFS format is supported in the multiaddress field in the smart contract, so
        // if the MultiAddress object can't be constructed, it means it is an HTTP address.
        try {
            MultiAddress address = new MultiAddress(Numeric.hexStringToByteArray(hexaString));
            return IPFS_GATEWAY_URI + address.toString();
        } catch (Exception e) {
            return BytesUtils.hexStringToAscii(hexaString);
        }
    }
}
