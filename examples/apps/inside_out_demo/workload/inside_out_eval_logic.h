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
#include "workload_processor.h"

size_t GetMaxFileSize();

size_t GetMaxIoResultSize();

std::string ReadFile(uint32_t handlerId, std::string fileName);

std::string WriteFile(uint32_t handlerId, std::string fileName,
    std::string content);

extern std::string ProcessRequest(std::string strIn);

