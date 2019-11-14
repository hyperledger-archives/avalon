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

#include "trusted_iohandler.h"
#include "iohandler_enclave.h"
#include "enclave_utils.h"

// Returns iohandler id corresponding to iohandler name
uint32_t GetIoHandlerId(const char* handlerName) {
    return TcfGetIoHandlerId(handlerName);
}

/*
  Opens given file and updates status in result buffer
  fileName - name of the file
  result - status of file open operation
  resultSize - Maximum size of the result buffer

*/
uint32_t FileOpen(uint32_t handlerId, std::string fileName, uint8_t *result,
    size_t resultSize) {
	uint32_t status;
	std::string fileOperation = "open";
	std::string command = fileOperation + " " + fileName;
	status = TcfExecuteIoCommand(handlerId, (const uint8_t *)command.c_str(),
            command.length(), result, resultSize, NULL, 0, NULL, 0);
	return status;
}

/*
  Closes given file and updates status in result buffer
  fileName - name of the file
  result - status of file close operation
  resultSize - Maximum size of the result buffer
  inBuf - buffer having file content
  inBufSize - max size of buffer having file content

*/
uint32_t FileClose(uint32_t handlerId, std::string fileName, uint8_t *result,
    size_t resultSize) {
	uint32_t status;
	std::string fileOperation = "close";
	std::string command = fileOperation + " " + fileName;
	status = TcfExecuteIoCommand(handlerId, (const uint8_t *)command.c_str(),
            command.length(), result, resultSize, NULL, 0, NULL, 0);
	return status;
}

/*
   Reads given file, stores content in out buffer
   and updates status in result buffer
   fileName - name of the file
   result - status of file read operation
   resultSize - Maximum size of the result buffer
   outBuf - buffer to hold file content
   outBufSize - max size of buffer having file content
*/
uint32_t FileRead(uint32_t handlerId, std::string fileName, uint8_t *result,
    size_t resultSize, uint8_t *outBuf, size_t outBufSize) {
	uint32_t status;
	std::string fileOperation = "read";
	std::string command = fileOperation + " " + fileName;
	status = TcfExecuteIoCommand(handlerId, (const uint8_t *)command.c_str(),
            command.length(), result, resultSize, NULL, 0, outBuf, outBufSize);
	return status;
}

/*
   Writes given file with content in input buffer
   and updates status in result buffer
   fileName - name of the file
   result - status of file write operation
   resultSize - Maximum size of the result buffer
   inBuf - buffer having file content to be written
   inBufSize - max size of buffer having file content
*/
uint32_t FileWrite(uint32_t handlerId, std::string fileName, uint8_t *result,
    size_t resultSize, const uint8_t *inBuf, size_t inBufSize) {
	uint32_t status;
	std::string fileOperation = "write";
	std::string command = fileOperation + " " + fileName;
	status = TcfExecuteIoCommand(handlerId, (const uint8_t *)command.c_str(),
            command.length(), result, resultSize, inBuf, inBufSize, NULL, 0);
	return status;
}

/*
   Tells current position of file pointer, stores it in out buffer
   and updates status in result buffer
   fileName - name of the file
   result - status of file ftell operation
   resultSize - Maximum size of the result buffer
   outBuf - buffer to hold position of file pointer
   outBufSize - max size of buffer having file content
*/
uint32_t FileTell(uint32_t handlerId, std::string fileName, uint8_t *result,
    size_t resultSize, uint8_t *outBuf, size_t outBufSize) {
	uint32_t status;
	std::string fileOperation = "tell";
	std::string command = fileOperation + " " + fileName;
	status = TcfExecuteIoCommand(handlerId, (const uint8_t *)command.c_str(),
            command.length(), result, resultSize, NULL, 0, outBuf, outBufSize);
	return status;
}


/*
   Places the file pointer to given position and updates status in result buffer
   fileName - name of the file
   result - status of file fseek operation
   resultSize - Maximum size of the result buffer
*/
uint32_t FileSeek(uint32_t handlerId, std::string fileName, size_t position,
    uint8_t *result, size_t resultSize) {
	uint32_t status;
	std::string fileOperation = "seek";
	std::string command = fileOperation + " " + fileName + " " +
            std::to_string(position);
	status = TcfExecuteIoCommand(handlerId, (const uint8_t *)command.c_str(),
            command.length(), result, resultSize, NULL, 0, NULL, 0);
	return status;
}

