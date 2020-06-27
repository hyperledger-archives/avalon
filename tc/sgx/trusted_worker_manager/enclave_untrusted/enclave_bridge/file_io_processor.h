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

#include <stdint.h>
#include <string>

using namespace std;

bool IsFileNameEmpty(string fileName, uint8_t *result, size_t resultSize);

// Below listed are the supported Inside-out File operations 

uint32_t FileOpen(string fileName, uint8_t *result, size_t resultSize);

uint32_t FileClose(string fileName, uint8_t *result, size_t resultSize);

uint32_t FileRead(string fileName, uint8_t *result, size_t resultSize,
    uint8_t *outBuf, size_t outBufSize);

uint32_t FileWrite(string fileName, uint8_t *result, size_t resultSize,
    const uint8_t *inBuf, size_t inBufSize);

uint32_t FileTell(string fileName, uint8_t *result, size_t resultSize,
    uint8_t *outBuf, size_t outBufSize);

uint32_t FileSeek(string fileName, size_t position, uint8_t *result,
    size_t resultSize);

uint32_t FileDelete(string fileName, uint8_t *result, size_t resultSize);
