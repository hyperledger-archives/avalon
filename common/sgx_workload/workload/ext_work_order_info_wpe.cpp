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


#include "ext_work_order_info_wpe.h"

ExtWorkOrderInfoWPE::ExtWorkOrderInfoWPE(void) {}

ExtWorkOrderInfoWPE::~ExtWorkOrderInfoWPE(void) {}

bool ExtWorkOrderInfoWPE::GetWorkorderSigningInfo(
    ByteArray& verification_key, ByteArray& requester_nonce,
    ByteArray& reserved_worker_nonce) {

    // To be implemented
    return true;
}  // ExtWorkOrderInfoWPE::GetWorkorderSigningInfo

bool ExtWorkOrderInfoWPE::SignWithWorkorderResultSigningKey(
    const ByteArray& message, ByteArray& signature,
    ByteArray& wo_temp_verification_key, ByteArray& wo_requester_nonce,
    ByteArray& wo_temp_verify_key_signature) {

    // To be implemented
    return true;
}  // ExtWorkOrderInfoWPE::SignWithWorkorderResultSigningKey
