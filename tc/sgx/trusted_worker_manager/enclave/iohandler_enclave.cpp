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

#include "enclave_common_t.h"
#include "tcf_error.h"
#include "error.h"
#include "iohandler_enclave.h"
#include "enclave_utils.h"


/**
 * Dummy ecall (non root function) to support an independent
 * interface for the iohandler.
 */
void ecall_dummy() {}


/**
 * Executes the given I/O command by invoking ocall and stores the result of
 * I/O execution in result buffer.
 *
 * @param handlerId   Identifier for iohandler
 * @param command     IO command that needs to be executed outside enclave
 * @param commandSize Size of the command buffer
 * @param result      Status of IO operation
 * @param resultSize  Maximum size of the result buffer
 * @param inBuf       Buffer having input data
 * @param inBufSize   Maximum size of buffer having input data
 * @param outBuf      Placeholder for output data
 * @param outBufSize  Maximum size of buffer having output data
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
            commandSize, result, resultSize, inBuf, inBufSize, outBuf,
            outBufSize);
    } catch (tcf::error::Error& e) {
        ocall_SetErrorMessage(e.what());
        status = e.error_code();
    } catch (...) {
        status = TCF_ERR_UNKNOWN;
    }

    return status;
}


/**
 * Returns iohandler ID corresponding to iohandler name.
 *
 * @param   handlerName Name of handler
 * @returns I/O handler ID. That is, 1 for handler "tcf-base-file-io"
 * @returns 0 on error
 */
uint32_t TcfGetIoHandlerId(const char* handlerName) {
    if (handlerName == "tcf-base-file-io") {
        return 1;
    }
    return 0;
}
