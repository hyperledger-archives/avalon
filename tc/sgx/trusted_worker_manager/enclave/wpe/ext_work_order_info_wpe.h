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

#include <stdlib.h>

#include "types.h"
#include "ext_work_order_info_impl.h"

class ExtWorkOrderInfoWPE : public ExtWorkOrderInfoImpl {
public:
    ExtWorkOrderInfoWPE(void);

    ~ExtWorkOrderInfoWPE(void);

    /*  Returns workorder request signing data, needed for cross-TEE processing
        Parameters:
            verification_key [OUT] - requester key used to sign the workorder
            requester_nonce [OUT] - nonce provided by the workorder requester
                                as part of the signature
            reserved_worker_nonce [OUT] - reserved for future to hold nonce
                                provided by the worker for this workorder
        Returns:
            true if the workorder was signed or false otherwise
    */
    bool GetWorkorderSigningInfo(
        ByteArray& verification_key, ByteArray& requester_nonce,
        ByteArray& reserved_worker_nonce);

    /* Reserved function to sign a message with same key(s) that
       will be used to sign the workorder result.

       Parameters:
           message - data to sign
           signature [OUT] - signature of the message
           wo_temp_verification_key [OUT] - temp verification key generated
                        for the work order response.
           wo_requester_nonce [OUT] - workorder requester nonce.
           wo_temp_verify_key_signature [OUT] - signature of the concatenation
                        of wo_requester_nonce and wo_temp_verification_key
     Returns:
        true on success or false otherwise
    */
    bool SignWithWorkorderResultSigningKey(
        const ByteArray& message, ByteArray& signature,
        ByteArray& wo_temp_verification_key, ByteArray& wo_requester_nonce,
        ByteArray& wo_temp_verify_key_signature);
};
