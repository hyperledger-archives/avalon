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
#include "enclave_utils.h"

std::string InsideOutEvalLogic::ReadFile(FileIoExecutor &file_io) {
    std::string out_buf;
    std::string result;

    size_t result_size = file_io.GetMaxIoResultSize();
    size_t out_buf_size = file_io.GetMaxFileSize();
    out_buf.reserve(out_buf_size);
    result.reserve(result_size);
    uint32_t status = file_io.FileRead((uint8_t *)result.c_str(), result_size,
        (uint8_t *)out_buf.c_str(), out_buf_size);

    if (status == 0) {
        Log(TCF_LOG_INFO, "File Read operation success. File content: %s",
            out_buf.c_str());
    }
    else {
	return result;
    }

    return out_buf;
}

std::string InsideOutEvalLogic::WriteFile(FileIoExecutor &file_io, std::string content) {
    std::string in_buf = content;
    std::string result;

    size_t result_size = file_io.GetMaxIoResultSize();
    result.reserve(result_size);
    uint32_t status = file_io.FileWrite((uint8_t *)result.c_str(), result_size,
        (const uint8_t *)in_buf.c_str(), in_buf.length());

    if (status == 0) {
        Log(TCF_LOG_INFO, "File Write operation success");
    }
    else {
        Log(TCF_LOG_ERROR, "File Write operation Failed");
    }
    return result;
}

std::string InsideOutEvalLogic::ProcessRequest(std::string str_in) {
    std::vector<std::string> args;
    char *saved_ptr;

    // tokenize input data
    char *token = strtok_r((char *)str_in.c_str(), " ", &saved_ptr);
    while(token) {
         args.push_back(token);
         token = strtok_r(NULL, " ", &saved_ptr);
    }

    FileIoExecutor file_io;
    uint32_t file_handler_id = file_io.GetIoHandlerId("tcf-base-file-io");
    file_io.SetIoHandlerId(file_handler_id);
    std::string io_result;

    if (args.size() > 0) {
        if (args.at(0) == "read") {
            if (args.size() == 2) {
                file_io.SetFileName(args.at(1));
                io_result = ReadFile(file_io);
            } else {
                io_result = "Insufficient arguments passed for i/o operation";
            }
        } else if (args.at(0) == "write") {
            if (args.size() == 3) {
                file_io.SetFileName(args.at(1));
                io_result = WriteFile(file_io, args.at(2));
            } else {
                io_result = "Insufficient arguments passed for i/o operation";
            }
        }
    } else {
        io_result = "Insufficient arguments passed for i/o operation";
    }

    return "RESULT: " + std::string(io_result.c_str());
}

