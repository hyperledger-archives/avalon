/* Copyright 2020 Intel Corporation
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
 * C++ non-class wrapper definitions for Avalon Inside-Out File I/O.
 * To use, #include "file_io_wrapper.h"
 */

#pragma once

#include <string>

// Read from given file return file data in string format
std::string Read(std::string file_name);

// Write given data to given file and return status
uint32_t Write(std::string file_name, std::string data);

// Delete given file
uint32_t Delete(std::string file_name);
