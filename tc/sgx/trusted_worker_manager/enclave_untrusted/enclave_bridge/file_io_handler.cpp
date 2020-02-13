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
#include <vector>
#include <iostream>
#include <string.h>

#include "file_io_handler.h"
#include "file_io_processor.h"

using namespace std;

uint32_t FileIoHandler::Process(uint32_t handlerId,
                                const uint8_t* command,
                                size_t commandSize,
                                uint8_t* result,
                                size_t resultSize,
                                const uint8_t* inBuf,
                                size_t inBufSize,
                                uint8_t* outBuf,
                                size_t outBufSize) {
        /* 
           based on the type of command (open/close/read/write/seek),
           call appropriate functions.
           Command format - "<Operation> <arg1> <arg2> ..."
           eg: "read filepath", "write filepath file-content", "seek filepath position"
        */

        vector<string> args;
        char *savedPtr;
        char *token = strtok_r( (char *)command, " ", &savedPtr);
        while (token) {
            args.push_back(token);
            token = strtok_r(NULL, " ", &savedPtr);
        }

        uint32_t status;
        if (args.at(0) == "open") {
            status = FileOpen(args[1], result, resultSize);
        } else if (args.at(0) == "close") {
            status = FileClose(args[1], result, resultSize);
        } else if (args.at(0) == "read") {
            status = FileRead(args[1], result, resultSize, outBuf, outBufSize);
        } else if (args.at(0) == "write") {
            status = FileWrite(args[1], result, resultSize, inBuf, inBufSize);
        } else if (args.at(0) == "seek") {
            status = FileSeek(args[1], stoi(args[2]), result, resultSize);
        } else if (args.at(0) == "tell") {
            status = FileTell(args[1], result, resultSize, outBuf, outBufSize);
        } else if (args.at(0) == "delete") {
            status = FileDelete(args[1], result, resultSize);
        } else {
            status = -1;
	}

	return status;
}

