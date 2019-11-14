/* Copyright 2019 Intel Corporation
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
#include <stdio.h>

#include "enclave_t.h"
#include "tcf_error.h"
#include "error.h"
#include "iohandler_enclave.h"
#include "enclave_utils.h"

/*
  Dummy ecall (non root function) to support independent
  interface for iohandler
*/
void ecall_dummy() {}

/*
  Executes given io command by invoking ocall and stores result of
  io execution in result buffer
  handlerId - identifier for iohandler
  command - IO command that needs to be executed outside enclave
  result - status of IO operation
  resultSize - Maximum size of the result buffer
  inBuf - buffer having input data
  inBufSize - max size of buffer having input data
  outBuf - placeholder for output data
  outBufSize - max size of buffer having output data
*/
uint32_t TcfExecuteIoCommand(uint32_t handlerId,
                             const uint8_t* command,
                             size_t commandSize,
                             uint8_t* result,
                             size_t resultSize,
                             const uint8_t* inBuf,
                             size_t inBufSize,
                             uint8_t* outBuf,
                             size_t outBufSize) {
    uint32_t status = 0;
    tcf::error::ThrowIfNull(command, "IO command is null");
    try {
        ocall_Process(&status, handlerId, (const char*) command,
            commandSize, result, resultSize, inBuf, inBufSize, outBuf, outBufSize);
    } catch (tcf::error::Error& e) {
        ocall_SetErrorMessage(e.what());
        status = e.error_code();
    } catch (...) {
        status = TCF_ERR_UNKNOWN;
    }

    return status;
}

// Returns iohandler id corresponding to iohandler name
uint32_t TcfGetIoHandlerId(const char* handlerName) {
    if (handlerName == "tcf-base-file-io") {
        return 1;
    }
    return 0;
}
