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

#include <unistd.h>
#include <functional>
#include <memory>
#include <string>
#include <iostream>
#include <sstream>

#include "sgx_uae_quote_ex.h"
#include "sgx_uae_epid.h"
#include "sgx_utility.h"
#include "enclave.h"

namespace tcf {

     namespace error {
        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        sgx_status_t ConvertErrorStatus(
            sgx_status_t ret,
            tcf_err_t tcfRet) {
            // If the Intel SGX code is success and the Avalon error code is
            // "busy", then convert to appropriate value.
            if ((SGX_SUCCESS == ret) &&
                (TCF_ERR_SYSTEM_BUSY == tcfRet)) {
                return SGX_ERROR_DEVICE_BUSY;
            }

            return ret;
        }  // ConvertErrorStatus
	// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    }  // namespace error

    namespace sgx_util {
        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        sgx_status_t CallSgx (std::function<sgx_status_t(void)> fxn,
                              const int retries,
                              const int retryDelayMs) {
            sgx_status_t ret = SGX_SUCCESS;
            int count = 0;
            bool retry = true;
            do {
                ret = fxn();
                if (SGX_ERROR_ENCLAVE_LOST == ret) {
                    // Enclave lost, potentially due to power state change
                    // reload the enclave and try again.
		    // Accessing global variable tcf::enclave_api::g_Enclave
		    // to reload the Enclave.
                    g_Enclave[0].LoadEnclave();
                } else if (SGX_ERROR_DEVICE_BUSY == ret) {
                    // Device is busy... wait and try again.
                    usleep(retryDelayMs  * 1000);
                    count++;
                    retry = count <= retries;
                } else {
                    // Not an error code we need to handle here,
                    // exit the loop and let the calling function handle it.
                    retry = false;
                }
            } while (retry);

            return ret;
        }  // CallSgx
	// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    }  /* namespace sgx_util */

}  /* namespace tcf */
