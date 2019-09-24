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

import org.bouncycastle.util.Arrays;
import org.web3j.crypto.Hash;
import org.web3j.utils.Numeric;

public class HashUtils {

    private HashUtils() {
        throw new UnsupportedOperationException();
    }

    public static String concatenateAndHash(String... hexaString) {

        // convert
        byte[] res = new byte[0];
        for (String str : hexaString) {
            res = Arrays.concatenate(res, BytesUtils.stringToBytes(str));
        }

        // Hash the result and convert to String
        return Numeric.toHexString(Hash.sha3(res));
    }
}
