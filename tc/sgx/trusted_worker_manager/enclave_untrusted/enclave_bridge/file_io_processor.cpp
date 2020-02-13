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
#include <fstream>
#include <iostream>
#include <string.h>
#include <stdio.h>

#include "file_io_processor.h"
#include "log.h"
#include "tcf_error.h"
#include "error.h"

#define SUCCESS 0
#define FAILED -1

using namespace std;

/*
    Validates if filename is empty
    fileName - name of the file
    result - status of file open operation
    resultSize - Maximum size of the result buffer
*/
bool IsFileNameEmpty(string fileName, uint8_t *result, size_t resultSize) {
    if (fileName.empty()) {
        std::string resultStr = "FAILED TO OPEN: Filename is empty";
        size_t resultStrSize = resultStr.length();
        result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
        tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize > resultSize, "result string size is "
                "greater than max result size");
        return true;
    }

    return false;
}

/*
    Opens file and updates status
    fileName - name of the file
    result - status of file open operation
    resultSize - Maximum size of the result buffer
*/
uint32_t FileOpen(string fileName, uint8_t *result, size_t resultSize) {
    string resultStr;
    size_t resultStrSize = 0;

    if ( IsFileNameEmpty(fileName, result, resultSize) ) {
        tcf::Log(TCF_LOG_ERROR, "Filename is empty\n");
        return FAILED;
    }

    try {
        ifstream fileStream (fileName);
        if (!fileStream.is_open()) {
            tcf::Log(TCF_LOG_ERROR, "Unable to open file %s\n", fileName.c_str());
            resultStr = "FAILED TO OPEN: Unable to open file";
            resultStrSize = resultStr.length();
            result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
            tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize < resultSize, "result string size is "
                "greater than max result size");
            fileStream.close();
            return FAILED;
        }
        tcf::Log(TCF_LOG_INFO, "File %s OPENED successfully\n", fileName.c_str());
        fileStream.close();

    } catch (std::exception e) {
        tcf::Log(TCF_LOG_ERROR, "Caught exception while opening file: %s\n", e.what());
        resultStr = "FAILED TO OPEN: Caught Exception while opening file";
        resultStrSize = resultStr.length();
        result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
        tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize < resultSize, "result string size is "
                "greater than max result size");
        return FAILED;
    }

    resultStr = "FILE OPEN SUCCESS";
    resultStrSize = resultStr.length();
    result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
    tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize < resultSize, "result string size is "
                "greater than max result size");
    return SUCCESS;
}

/* 
    Closes file and updates status
    fileName - name of the file
    result - status of file close operation
    resultSize - Maximum size of the result buffer
    inBuf - buffer having file content
    inBufSize - max size of buffer having file content
*/
uint32_t FileClose(std::string fileName, uint8_t *result, size_t resultSize) {
    string resultStr;
    size_t resultStrSize = 0;

    if ( IsFileNameEmpty(fileName, result, resultSize) ) {
        tcf::Log(TCF_LOG_ERROR, "Filename is empty\n");
        return FAILED;
    }

    try {
        ifstream fileStream (fileName);
        if (!fileStream.is_open()) {
            tcf::Log(TCF_LOG_ERROR, "Unable to close file %s\n", fileName.c_str());
            resultStr = "FAILED TO CLOSE: Unable to close file";
            resultStrSize = resultStr.length();
            result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
            tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize < resultSize, "result string size is "
                "greater than max result size");
            return FAILED;
        }

        fileStream.close();
        tcf::Log(TCF_LOG_INFO, "File %s CLOSED successfully\n", fileName.c_str());

    } catch (std::ifstream::failure e) {
            tcf::Log(TCF_LOG_ERROR, "Caught exception while Closing file: %s\n", e.what());
            resultStr = "FAILED TO CLOSE: Caught exception while closing file";
            resultStrSize = resultStr.length();
            result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
            tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize < resultSize, "result string size is "
                "greater than max result size");
            return FAILED;
    }

    resultStr = "FILE CLOSE SUCCESS";
    resultStrSize = resultStr.length();
    result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
    tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize < resultSize, "result string size is "
                "greater than max result size");
    return SUCCESS;
}

/*
   Reads file, store content of file in buffer and updates status
   fileName - name of the file
   result - status of file read operation
   resultSize - Maximum size of the result buffer
   outBuf - buffer to hold file content
   outBufSize - max size of buffer having file content
*/
uint32_t FileRead(std::string fileName, uint8_t *result, size_t resultSize,
    uint8_t *outBuf, size_t outBufSize) {
    string resultStr;
    size_t resultStrSize = 0;

    if ( IsFileNameEmpty(fileName, result, resultSize) ) {
        tcf::Log(TCF_LOG_ERROR, "Filename is empty\n");
        return FAILED;
    }

    try {
        ifstream fileStream (fileName);
        if (!fileStream.is_open())
        {
            tcf::Log(TCF_LOG_ERROR, "Unable to open file %s\n", fileName.c_str());
            resultStr = "FAILED TO READ: Unable to open file";
            resultStrSize = resultStr.length();
            result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
            tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize > resultSize, "result string size is "
                "greater than max result size");
            fileStream.close();
            return FAILED;
        }

        fileStream.seekg (0, fileStream.end);
        int fileLen = fileStream.tellg();
        fileStream.seekg (0, fileStream.beg);

        char *buff = new char[fileLen];
        fileStream.read(buff, fileLen);

        if ( !fileStream) {
            tcf::Log(TCF_LOG_ERROR, "Failed to read complete file %s\n", fileName.c_str());
            resultStr = "FAILED TO READ: Couldn't read complete file";
            resultStrSize = resultStr.length();
            result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
            tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize > resultSize, "result string size is "
                "greater than max result size");
            fileStream.close();
            return FAILED;
        }

       tcf::Log(TCF_LOG_ERROR, "File %s read has been completed\n", fileName.c_str());

       // Copy the read file content to output buffer
       outBuf = (uint8_t *)strncpy((char *)outBuf, buff, fileLen);
       tcf::error::ThrowIf<tcf::error::ValueError>(
                strlen((char*)outBuf) > outBufSize, "size of outBuf is "
                "greater than max outBufSize");
       delete[] buff;
       fileStream.close();

    } catch (std::ifstream::failure e) {
         tcf::Log(TCF_LOG_ERROR, "Caught exception while Reading file: %s\n", e.what());
         resultStr = "FAILED TO READ: Caught Exception while reading file";
         resultStrSize = resultStr.length();
         result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
         tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize > resultSize, "result string size is "
                "greater than max result size");
         return FAILED;
    }

    resultStr = "FILE READ SUCCESS";
    resultStrSize = resultStr.length();
    result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
    tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize > resultSize, "result string size is "
                "greater than max result size");

    return SUCCESS;
}

/* 
   Writes file with the content of the buffer and updates status
   fileName - name of the file
   result - status of file write operation
   resultSize - Maximum size of the result buffer
   inBuf - buffer having file content to be written
   inBufSize - max size of buffer having file content  
*/ 
uint32_t FileWrite(std::string fileName, uint8_t *result, size_t resultSize,
    const uint8_t *inBuf, size_t inBufSize) {
    string resultStr;
    size_t resultStrSize = 0;

    if ( IsFileNameEmpty(fileName, result, resultSize) ) {
        tcf::Log(TCF_LOG_ERROR, "Filename is empty\n");
        return FAILED;
    }

    try {
        ofstream fileStream (fileName);
        if (!fileStream.is_open()) {
            tcf::Log(TCF_LOG_ERROR, "Unable to open file %s\n", fileName.c_str());
            resultStr = "FAILED TO WRITE: Unable to open file";
            resultStrSize = resultStr.length();
            result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
            tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize > resultSize, "result string size is "
                "greater than max result size");
            return FAILED;
        }

        // write buffer data to file
        fileStream.write((const char*)inBuf, inBufSize);
        tcf::Log(TCF_LOG_INFO, "File %s WRITE has been completed\n", fileName.c_str());
        fileStream.close();

    } catch (std::ofstream::failure e) {
        tcf::Log(TCF_LOG_ERROR, "Caught exception while Writing file: %s\n", e.what());
        resultStr = "FAILED TO WRITE: Caught Exception while writing file";
        resultSize = resultStr.length();
        result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
        tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize > resultSize, "result string size is "
                "greater than max result size");
        return FAILED;
    }

    resultStr = "FILE WRITE SUCCESS";
    resultStrSize = resultStr.length();
    result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
    tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize > resultSize, "result string size is "
                "greater than max result size");
    return SUCCESS;
}

/*
   Tells current position of the file pointer and stores it in buffer
   fileName - name of the file
   result - status of file ftell operation
   resultSize - Maximum size of the result buffer
   outBuf - buffer to hold position of file pointer
   outBufSize - max size of buffer having file content
*/
uint32_t FileTell(std::string fileName, uint8_t *result, size_t resultSize,
    uint8_t *outBuf, size_t outBufSize) {
    string resultStr;
    size_t resultStrSize = 0;

    if ( IsFileNameEmpty(fileName, result, resultSize) ) {
        tcf::Log(TCF_LOG_ERROR, "Filename is empty\n");
        return FAILED;
    }

    try {
        ifstream fileStream (fileName);
        if (!fileStream.is_open()) {
            tcf::Log(TCF_LOG_ERROR, "Unable to open file %s\n", fileName.c_str());
            resultStr = "FAILED TO FTELL: Unable to open file";
            resultStrSize = resultStr.length();
            result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
            tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize > resultSize, "result string size is "
                "greater than max result size");
            fileStream.close();
            return FAILED;
        }

        size_t index = fileStream.tellg();

        tcf::Log(TCF_LOG_INFO, "File %s ftell has been completed\n", fileName.c_str());
        outBuf = (uint8_t*) index;
        tcf::error::ThrowIf<tcf::error::ValueError>(
                strlen((char*)outBuf) > outBufSize, "size of outBuf is "
                "greater than max outBufSize");
        fileStream.close();

    } catch (std::ifstream::failure e) {
        tcf::Log(TCF_LOG_ERROR, "Caught exception while ftell file: %s\n", e.what());
        resultStr = "FAILED TO FTELL: Caught Exception while doing ftell";
        resultStrSize = resultStr.length();
        result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
        tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize > resultSize, "result string size is "
                "greater than max result size");
        return FAILED;
    }

    resultStr = "FILE FTELL SUCCESS";
    resultStrSize = resultStr.length();
    result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
    tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize > resultSize, "result string size is "
                "greater than max result size");
    return SUCCESS;
}

/*
    Places file pointer to the specific position updates status
    fileName - name of the file
    result - status of file fseek operation
    resultSize - Maximum size of the result buffer
*/
uint32_t FileSeek(std::string fileName, size_t position, uint8_t *result,
    size_t resultSize) {
    string resultStr;
    size_t resultStrSize = 0;

    if ( IsFileNameEmpty(fileName, result, resultSize) ) {
        tcf::Log(TCF_LOG_ERROR, "Filename is empty\n");
        return FAILED;
    }

    try {
        ifstream fileStream (fileName);
        if (!fileStream.is_open()) {
            tcf::Log(TCF_LOG_ERROR, "Unable to open file %s\n", fileName.c_str());
            resultStr = "FAILED TO FSEEK: Unable to open file";
            resultStrSize = resultStr.length();
            result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
            tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize > resultSize, "result string size is "
                "greater than max result size");
            fileStream.close();
            return FAILED;
        }

        fileStream.seekg(position, ios::beg);
        tcf::Log(TCF_LOG_INFO, "File %s fseek has been completed\n", fileName.c_str());
        fileStream.close();

    } catch (std::ifstream::failure e) {
        tcf::Log(TCF_LOG_ERROR, "Caught exception while fseek file: %s", e.what());
        resultStr = "FAILED TO FSEEK: Caught Exception while doing fseek";
        resultStrSize = resultStr.length();
        result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
        tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize > resultSize, "result string size is "
                "greater than max result size");
        return FAILED;
    }

    resultStr = "FILE FSEEK SUCCESS";
    resultStrSize = resultStr.length();
    result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
    tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize > resultSize, "result string size is "
                "greater than max result size");
    return SUCCESS;
}

uint32_t FileDelete(string fileName, uint8_t *result, size_t resultSize) {
    string resultStr;
    size_t resultStrSize = 0;

    if ( IsFileNameEmpty(fileName, result, resultSize) ) {
        tcf::Log(TCF_LOG_ERROR, "Filename is empty\n");
        return FAILED;
    }

    try {
        if ( remove(fileName.c_str()) != 0 ) {
            tcf::Log(TCF_LOG_DEBUG, "File %s delete failed", fileName.c_str());
            resultStr = "FILE DELETE FAILED";
            resultStrSize = resultStr.length();
            tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize > resultSize, "result string size is "
                "greater than max result size");
            result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
        }
    } catch ( std::exception e ) {
        tcf::Log(TCF_LOG_ERROR, "Caught exception while deleting file: %s\n", e.what());
        resultStr = "FAILED TO DELETE: Caught Exception while deleting file";
        resultStrSize = resultStr.length();
        tcf::error::ThrowIf<tcf::error::ValueError>(
                resultStrSize < resultSize, "result string size is "
                "greater than max result size");
        result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
        return FAILED;
    }

    tcf::Log(TCF_LOG_DEBUG, "File %s delete successful", fileName.c_str());
    resultStr = "FILE DELETE SUCCESS";
    resultStrSize = resultStr.length();
    tcf::error::ThrowIf<tcf::error::ValueError>(
        resultStrSize > resultSize, "result string size is "
        "greater than max result size");
    result = (uint8_t *)strncpy((char *)result, resultStr.c_str(), resultStrSize);
    return SUCCESS;
}
