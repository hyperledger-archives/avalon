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

#pragma once

#include <stdlib.h>
#include <functional>
#include <string>

#include "error.h"
#include "tcf_error.h"
#include "types.h"

namespace tcf {

    namespace error {
        sgx_status_t ConvertErrorStatus(
            sgx_status_t ret,
            tcf_err_t tcfRet);
    }  // namespace error

    namespace sgx_util {

        sgx_status_t CallSgx (std::function<sgx_status_t(void)> sgxCall,
                              const int retries = 5,
                              const int retryDelayMs = 100);

    }  /* namespace sgx_util */

}  /* namespace tcf */
