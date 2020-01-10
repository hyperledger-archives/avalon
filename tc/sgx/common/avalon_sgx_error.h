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

#include <stdexcept>

#include "sgx_error.h"

namespace tcf {
    namespace error {
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        class SgxError : public std::exception {
        public:
            explicit SgxError() : errorCode(SGX_SUCCESS) {}
            explicit SgxError(
                sgx_status_t inErrorCode
                ) :
                errorCode(inErrorCode) {}
            virtual ~SgxError() {}

            sgx_status_t error() { return errorCode; }

            virtual char const * what() const throw() {
                return "Sgx Call Failed.";
            }

        private:
            sgx_status_t errorCode;
        }; // class SgxError

        // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        void ThrowSgxError(
            sgx_status_t ret,
            const char* msg = nullptr
            );

    }  // error
}  // tcf
