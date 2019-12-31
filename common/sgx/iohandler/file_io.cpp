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
#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <stdint.h>

#include "file_io.h"
#include "iohandler_enclave.h"
#include "enclave_utils.h"

#define MAX_FILE_SIZE 1024
#define MAX_IO_RESULT_SIZE 128

// Returns iohandler id corresponding to iohandler name
uint32_t FileIoExecutor::GetIoHandlerId(const char* handler_name) {
    return TcfGetIoHandlerId(handler_name);
}

// Maximum size of buffer that is used for file io
size_t FileIoExecutor::GetMaxFileSize() {
    return MAX_FILE_SIZE;
}

// Maximum size of result buffer that is used to store status of io
size_t FileIoExecutor::GetMaxIoResultSize() {
    return MAX_IO_RESULT_SIZE;
}

/*
  Opens given file and updates status in result buffer
  result - status of file open operation
  result_size - Maximum size of the result buffer

*/
uint32_t FileIoExecutor::FileOpen(uint8_t *result, size_t result_size) {
    uint32_t status;
    std::string file_operation = "open";
    std::string command = file_operation + " " + this->file_name;
    status = TcfExecuteIoCommand(this->handler_id, (const uint8_t *)command.c_str(),
        command.length(), result, result_size, NULL, 0, NULL, 0);
    return status;
}

/*
  Closes given file and updates status in result buffer
  result - status of file close operation
  result_size - Maximum size of the result buffer
*/
uint32_t FileIoExecutor::FileClose(uint8_t *result, size_t result_size) {
    uint32_t status;
    std::string file_operation = "close";
    std::string command = file_operation + " " + this->file_name;
    status = TcfExecuteIoCommand(this->handler_id, (const uint8_t *)command.c_str(),
        command.length(), result, result_size, NULL, 0, NULL, 0);
    return status;
}

/*
   Reads given file, stores content in out buffer
   and updates status in result buffer
   result - status of file read operation
   result_size - Maximum size of the result buffer
   out_buf - buffer to hold file content
   out_buf_size - max size of buffer having file content
*/
uint32_t FileIoExecutor::FileRead(uint8_t *result, size_t result_size,
    uint8_t *out_buf, size_t out_buf_size) {
    uint32_t status;
    std::string file_operation = "read";
    std::string command = file_operation + " " + this->file_name;
    status = TcfExecuteIoCommand(this->handler_id,
        (const uint8_t *)command.c_str(), command.length(), result, result_size,
        NULL, 0, out_buf, out_buf_size);
    return status;
}

/*
   Writes given file with content in input buffer
   and updates status in result buffer
   result - status of file write operation
   result_size - Maximum size of the result buffer
   in_buf - buffer having file content to be written
   in_buf_size - max size of buffer having file content
*/
uint32_t FileIoExecutor::FileWrite(uint8_t *result, size_t result_size,
    const uint8_t *in_buf, size_t in_buf_size) {
    uint32_t status;
    std::string file_operation = "write";
    std::string command = file_operation + " " + this->file_name;
    status = TcfExecuteIoCommand(this->handler_id,
        (const uint8_t *)command.c_str(), command.length(), result, result_size,
        in_buf, in_buf_size, NULL, 0);
    return status;
}

/*
   Tells current position of file pointer, stores it in out buffer
   and updates status in result buffer
   result - status of file ftell operation
   result_size - Maximum size of the result buffer
   out_buf - buffer to hold position of file pointer
   out_buf_size - max size of buffer having file content
*/
uint32_t FileIoExecutor::FileTell(uint8_t *result, size_t result_size,
    uint8_t *out_buf, size_t out_buf_size) {
    uint32_t status;
    std::string file_operation = "tell";
    std::string command = file_operation + " " + this->file_name;
    status = TcfExecuteIoCommand(this->handler_id,
        (const uint8_t *)command.c_str(), command.length(), result, result_size,
        NULL, 0, out_buf, out_buf_size);
    return status;
}


/*
   Places the file pointer to given position and updates status in result buffer
   result - status of file fseek operation
   result_size - Maximum size of the result buffer
*/
uint32_t FileIoExecutor::FileSeek(size_t position, uint8_t *result, size_t result_size) {
    uint32_t status;
    std::string file_operation = "seek";
    std::string command = file_operation + " " + this->file_name + " " +
        std::to_string(position);
    status = TcfExecuteIoCommand(this->handler_id,
        (const uint8_t *)command.c_str(), command.length(), result, result_size,
        NULL, 0, NULL, 0);
    return status;
}
