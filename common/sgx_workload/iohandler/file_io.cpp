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

/**
 * @file
 * FileIoExecutor C++ class implementation for Avalon Inside-Out File I/O.
 * To use, #include "file_io.h"
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


/**
 * Get the I/O handler ID corresponding to IoHandler handler_name.
 *
 * @param   handlerName Name of handler
 * @returns I/O handler ID. That is, 1 for handler "tcf-base-file-io"
 * @returns 0 on error
 */
uint32_t FileIoExecutor::GetIoHandlerId(const char* handler_name) {
    return TcfGetIoHandlerId(handler_name);
}


/**
 * Get the maximum size of the buffer used for file I/O.
 *
 * @returns Maximum buffer size in bytes
 */
size_t FileIoExecutor::GetMaxFileSize() {
    return MAX_FILE_SIZE;
}


/**
 * Get the maximum size of the result buffer used to store the
 * I/O status.
 *
 * @returns Maximum result buffer size in bytes
 */
size_t FileIoExecutor::GetMaxIoResultSize() {
    return MAX_IO_RESULT_SIZE;
}


/**
 * Opens given file and updates status in the result buffer.
 *
 * @param result      Status of file open operation (0 is success,
 *                    non-0 is failure)
 * @param result_size Maximum size of the result buffer in bytes
 * @returns           Status of operation (0 on success, non-0 on failure)
 */
uint32_t FileIoExecutor::FileOpen(uint8_t *result, size_t result_size) {
    uint32_t status;
    std::string file_operation = "open";
    std::string command = file_operation + " " + this->file_name;
    status = TcfExecuteIoCommand(this->handler_id,
        (const uint8_t *)command.c_str(),
        command.length(), result, result_size, NULL, 0, NULL, 0);
    return status;
}


/**
 * Closes given file and updates status in the result buffer.
 *
 * @param result      Status of file close operation (0 is success,
 *                    non-0 is failure)
 * @param result_size Maximum size of the result buffer in bytes
 * @returns           Status of operation (0 on success, non-0 on failure)
 */
uint32_t FileIoExecutor::FileClose(uint8_t *result, size_t result_size) {
    uint32_t status;
    std::string file_operation = "close";
    std::string command = file_operation + " " + this->file_name;
    status = TcfExecuteIoCommand(this->handler_id,
        (const uint8_t *)command.c_str(),
        command.length(), result, result_size, NULL, 0, NULL, 0);
    return status;
}


/**
 * Reads given file, stores content in out buffer
 * and updates status in result buffer.
 *
 * @param result       Status of file read operation (0 is success,
 *                     non-0 is failure)
 * @param result_size  Maximum size of the result buffer in bytes
 * @param out_buf      Buffer to hold file content
 * @param out_buf_size Maximum size of out_buf to contain the file contents
 *                     in bytes
 * @returns            Status of operation (0 on success, non-0 on failure)
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


/**
 * Writes given file with content in input buffer
 * and updates status in result buffer.
 *
 * @param result      Status of file write operation (0 is success,
 *                    non-0 is failure)
 * @param result_size Maximum size of the result buffer in bytes
 * @param in_buf      Buffer with content to be written to the file
 * @param in_buf_size Maximum size of in_buf to write to the file in bytes
 * @returns           Status of operation (0 on success, non-0 on failure)
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


/**
 * Gets the current position of the file, stores it in buffer out_buf,
 * and updates status in result buffer.
 *
 * @param result       status of file tell operation (0 is success,
 *                     non-0 is failure)
 * @param result_size  Maximum size of the result buffer in bytes
 * @param out_buf      Buffer to hold file position
 * @param out_buf_size Maximum size of out_buf to contain the file position
 *                     in bytes
 * @returns            Status of operation (0 on success, non-0 on failure)
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


/**
 * Moves the file position the file to the given position and
 * updates the status in result buffer.
 *
 * @param position    Byte offset of new file position
 * @param result      Status of file seek operation (0 is success,
 *                    non-0 is failure)
 * @param result_size Maximum size of the result buffer in bytes
 * @returns           Status of operation (0 on success, non-0 on failure)
 */
uint32_t FileIoExecutor::FileSeek(size_t position, uint8_t *result,
        size_t result_size) {
    uint32_t status;
    std::string file_operation = "seek";
    std::string command = file_operation + " " + this->file_name + " " +
        std::to_string(position);
    status = TcfExecuteIoCommand(this->handler_id,
        (const uint8_t *)command.c_str(), command.length(), result, result_size,
        NULL, 0, NULL, 0);
    return status;
}


/**
 * Deletes the file whose name is stored in the FileIoExecutor instance.
 *
 * @param result      Status of file delete operation (0 is success,
 *                    non-0 is failure)
 * @param result_size Maximum size of the result buffer in bytes
 * @returns           Status of operation (0 on success, non-0 on failure)
 */
uint32_t FileIoExecutor::FileDelete(uint8_t *result, size_t result_size) {
    uint32_t status;
    std::string file_operation = "delete";
    std::string command = file_operation + " " + this->file_name;
    status = TcfExecuteIoCommand(this->handler_id,
        (const uint8_t *)command.c_str(), command.length(), result, result_size,
        NULL, 0, NULL, 0);
    return status;
}
