/* Copyright 2020 Intel Corporation
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
*/

#include "types.h"

class ExtWorkOrderInfo {
public:
    enum KeyType
    {
        KeyType_None = 0,
        KeyType_SECP256K1 = 1
    };

    /* Parameters:
           data [OUT] - workorder extended data (if present) or it is not used
       Returns:
           size of the workorder extra data or null if none is provided
    */
    virtual size_t GetWorkOrderExData(ByteArray& data) = 0;

    /* Verifies an attestation info and returns its MRENCLAVE,
       MRSIGNER, Encryption Key, Verification Key on success.
     Parameters:
        attestation_data - attestation to verify
        mrenclave [OUT] - MRENCLAVE value from the attestation_data
                          on success or not used
        mrsigner [OUT] - MRSIGNER value from the attestation_data
                         on success or not used
        encryption_pub_key [OUT] - public encryption key from the
                                   attestation_data on success or not used
        verification_key [OUT] - public verification key from the
                                 attestation_data on success or not used
     Returns:
        zero on success or an error code otherwise
    */
    virtual int VerifyAttestation(const ByteArray& attestation_data,
        ByteArray& mrenclave,
        ByteArray& mrsigner,
        ByteArray& verification_key,
        ByteArray& encryption_pub_key) = 0;
};  // ExtWorkOrderInfo
