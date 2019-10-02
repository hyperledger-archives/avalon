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
