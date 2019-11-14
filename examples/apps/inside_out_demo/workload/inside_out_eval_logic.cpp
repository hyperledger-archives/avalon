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

#include <string>
#include <string.h>
#include <stdint.h>
#include <stdarg.h>
#include <vector>

#include "inside_out_eval_logic.h"
#include "trusted_iohandler.h"
#include "enclave_utils.h"

// Maximum size of buffer that is used for file io
size_t GetMaxFileSize() {
    return 1024;
}

// Maximum size of result buffer that is used to store status of io
size_t GetMaxIoResultSize() {
    return 128;
}

std::string ReadFile(uint32_t handlerId, std::string fileName) {
    std::string outBuf;
    std::string result;
    size_t resultSize = GetMaxIoResultSize();
    size_t outBufSize = GetMaxFileSize();
    outBuf.reserve(outBufSize);
    result.reserve(resultSize);
    uint32_t status = FileRead(handlerId, fileName, (uint8_t *)result.c_str(),
        resultSize, (uint8_t *)outBuf.c_str(), outBufSize);

    if (status == 0) {
        Log(TCF_LOG_INFO, "File Read operation success. File content: %s",
            outBuf.c_str());
    }
    else {
	return result;
    }

    return outBuf;
}

std::string WriteFile(uint32_t handlerId, std::string fileName, std::string content) {
    std::string inBuf = content;

    std::string result;
    size_t resultSize = GetMaxIoResultSize();
    result.reserve(resultSize);
    uint32_t status = FileWrite(handlerId, fileName, (uint8_t *)result.c_str(),
        resultSize, (const uint8_t *)inBuf.c_str(), inBuf.length());

    if (status == 0) {
        Log(TCF_LOG_INFO, "File Write operation success");
    }
    else {
        Log(TCF_LOG_ERROR, "File Write operation Failed");
    }
    return result;
}

std::string ProcessRequest(std::string strIn) {
    std::vector<std::string> args;
    char *savedPtr;

    // tokenize input data
    char *token = strtok_r((char *)strIn.c_str(), " ", &savedPtr);
    while(token) {
         args.push_back(token);
         token = strtok_r(NULL, " ", &savedPtr);
    }

    uint32_t fileHandlerId = GetIoHandlerId("tcf-base-file-io");
    std::string ioResult;

    if (args.size() > 0) {
        if (args.at(0) == "read") {
            if (args.size() == 2) {
                ioResult = ReadFile(fileHandlerId, args.at(1));
            } else {
                ioResult = "Insuffient arguments passed for i/o operation";
            }
        } else if (args.at(0) == "write") {
            if (args.size() == 3) {
                ioResult = WriteFile(fileHandlerId, args.at(1), args.at(2));
            } else {
                ioResult = "Insuffient arguments passed for i/o operation";
            }
        }
    } else {
        ioResult = "Insuffient arguments passed for i/o operation";
    }

    return "RESULT: " + std::string(ioResult.c_str()); 
}

