/* Copyright 2018 Intel Corporation
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

#include "enclave_common_u.h"

#include <stdio.h>
#include <algorithm>
#include <string>
#include <vector>

#include "error.h"
#include "avalon_sgx_error.h"
#include "log.h"
#include "tcf_error.h"
#include "types.h"
#include "zero.h"

#include "enclave.h"
#include "base.h"
#include "signup.h"

#include "sgx_utility.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
size_t SignupData::CalculateSealedEnclaveDataSize(void) {
    size_t sealed_data_size = 0;

    tcf_err_t presult = TCF_SUCCESS;
    sgx_status_t sresult;

    // Get the enclave id for passing into the ecall
    sgx_enclave_id_t enclaveid = g_Enclave[0].GetEnclaveId();

    sresult = tcf::sgx_util::CallSgx(
            [ enclaveid,
              &presult,
              &sealed_data_size ] () {
                sgx_status_t ret =
                ecall_CalculateSealedEnclaveDataSize(
                    enclaveid,
                    &presult,
                    &sealed_data_size);
                return tcf::error::ConvertErrorStatus(ret, presult);
            });
    tcf::error::ThrowSgxError(sresult,
        "Intel SGX enclave call failed (ecall_CalculateSealedEnclaveDataSize)");
    g_Enclave[0].ThrowTCFError(presult);

    return sealed_data_size;
}  // SignupData::CalculateSealedEnclaveDataSize


// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
size_t SignupData::CalculatePublicEnclaveDataSize(void) {
    size_t public_data_size = 0;

    tcf_err_t presult = TCF_SUCCESS;
    sgx_status_t sresult;

    // Get the enclave id for passing into the ecall
    sgx_enclave_id_t enclaveid = g_Enclave[0].GetEnclaveId();

    sresult = tcf::sgx_util::CallSgx(
            [ enclaveid,
              &presult,
              &public_data_size ] () {
                sgx_status_t ret =
                ecall_CalculatePublicEnclaveDataSize(
                    enclaveid,
                    &presult,
                    &public_data_size);
                return tcf::error::ConvertErrorStatus(ret, presult);
            });
    tcf::error::ThrowSgxError(sresult,
        "Intel SGX enclave call failed (ecall_CalculatePublicEnclaveDataSize)");
    g_Enclave[0].ThrowTCFError(presult);

    return public_data_size;
}  // SignupData::CalculatePublicEnclaveDataSize
