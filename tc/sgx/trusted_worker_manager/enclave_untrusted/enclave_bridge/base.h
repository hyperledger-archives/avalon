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

#pragma once

#include <stdlib.h>
#include <string>

#include "error.h"
#include "tcf_error.h"
#include "types.h"
#include "enclave_queue.h"
#include "attestation.h"

namespace tcf {
    namespace enclave_api {
        namespace base {

            /*
              Tests if libtcf is built against the Intel SGX simulator or the
              Intel SGX runtime
            */
            int IsSgxSimulator();

            /*
              Returns an object with index of next available enclave as a field
              Ensures enclave index is returned to queue in case of a crash
            */
            tcf::enclave_queue::ReadyEnclave GetReadyEnclave();

            /*
              Saves an error message for later retrieval.
             */
            void SetLastError(
                const std::string& message = "No description given");

            /*
              Returns the string associated with the last Avalon error message.
            */
            std::string GetLastError(void);

            /*
              Start Avalon services

              inPathToEnclave - A pointer to a string that contains the path
              to the enclave DLL.
              inSpid - A pointer to a string that contains the hex encoded SPID.
              persisted_sealed_data - Sealed data persisted from last bootup
              numOfEnclaves -- Number of worker enclaves to create
            */
            tcf_err_t Initialize(const std::string& inPathToEnclave,
                const tcf::attestation::Attestation *attestation,
                const std::string& persisted_sealed_data,
                const int numOfEnclaves);

            /*
              Stop Avalon services
            */
            tcf_err_t Terminate();

            /*
              Helper functions to determine buffer sizes for outgoing buffers
              filled in by enclave.
            */

            size_t GetSignatureSize();
            size_t GetEnclaveQuoteSize();

            /*
              Returns characteristics about the enclave that can be used later
              when verifying signup information from other validators,

              outMrEnclave - A pointer to a buffer that upon return will
              contain the hex encoded enclave hash (aka, mr_enclave).
              inMrEnclaveLength - The size of the buffer pointed to by
              outMrEnclave.
              The value to provide for this parameter may be obtained by
              calling GetEnclaveMeasurementSize().
              outEnclaveBasename - A pointer to a buffer that upon return will
              contain the hex encoded enclave basename.
              inEnclaveBasenameLength - The size of the buffer pointed to by
              outEnclaveBasename. The value to provide for this parameter may
              be obtained by calling GetEnclaveBasenameSize().
            */
            tcf_err_t GetEnclaveCharacteristics(
                HexEncodedString& outMrEnclave,
                HexEncodedString& outEnclaveBasename);

        }  /* namespace base */

    }  /* namespace enclave_api */

}  /* namespace tcf */
