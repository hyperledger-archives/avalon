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
#include <string>
#include <stdint.h>
#include <iostream>

#include "file_io_handler.h"

extern "C" {
	
    uint32_t ocall_Process(uint32_t handlerId,
                           const char* command,
                           size_t commandSize,
                           uint8_t* result,
                           size_t resultSize,
                           const uint8_t* inBuf,
                           size_t inBufSize,
                           uint8_t* outBuf,
                           size_t outBufSize) {  
        uint32_t status = 0;
        if ( handlerId == 1 ) {
            FileIoHandler fileIo;
            status = fileIo.Process(handlerId, (const uint8_t*) command,
                commandSize, result, resultSize, inBuf, inBufSize,
                outBuf, outBufSize);
        }

        return status;

    }
}

